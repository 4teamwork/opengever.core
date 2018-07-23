from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.role_assignments import ProtectDossierRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.dossier import _
from opengever.ogds.base.sources import AllUsersAndGroupsSourceBinder
from plone import api
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.annotation import AnnotationsFactoryImpl
from plone.behavior.annotation import AnnotationStorage
from plone.behavior.interfaces import ISchemaAwareFactory
from plone.supermodel import model
from Products.CMFPlone.utils import safe_unicode
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def current_user(context):
    userid = api.user.get_current().getId()

    if not userid:
        return None

    try:
        AllUsersAndGroupsSourceBinder()(context).getTerm(userid)
    except LookupError:
        # The current logged in user does not exist in the
        # field-source.
        return None

    if 'Manager' in api.user.get_roles():
        # We don't want to prefill managers.
        return None

    return safe_unicode(userid)


class IProtectDossierMarker(Interface):
    """Marker interface for the protect dossier behavior"""


class IProtectDossier(model.Schema):
    """Define a form for managing dossier protection."""

    model.fieldset(
        u'protect',
        label=_(
            u'fieldset_protect',
            default=u'Protect',
            ),
        fields=[
            'reading',
            'reading_and_writing',
            'dossier_manager',
            ],
        )

    form.widget(
        'reading',
        KeywordFieldWidget,
        async=True,
        template_result='usersAndGroups',
        template_selection='usersAndGroups',
        )

    form.write_permission(
        reading='opengever.dossier.ProtectDossier',
        )

    reading = schema.List(
        title=_(
            u'label_reading',
            default=u'Reading',
            ),
        description=_(
            u'description_reading',
            default=(
                u'Choose users and groups which have only readable access to '
                u'the dossier'
                ),
            ),
        value_type=schema.Choice(
            source=AllUsersAndGroupsSourceBinder(),
            ),
        required=False,
        default=[],
        missing_value=[],
        )

    form.widget(
        'reading_and_writing',
        KeywordFieldWidget,
        async=True,
        template_selection='usersAndGroups',
        template_result='usersAndGroups',
        )
    form.write_permission(
        reading_and_writing='opengever.dossier.ProtectDossier',
        )

    reading_and_writing = schema.List(
        title=_(
            u'label_reading_and_writing',
            default=u'Reading and writing',
            ),
        description=_(
            u'description_reading_and_writing',
            default=(
                u'Choose users and groups which have readable and writing '
                u'access to the dossier'
                ),
            ),
        value_type=schema.Choice(
            source=AllUsersAndGroupsSourceBinder(),
            ),
        required=False,
        default=[],
        missing_value=[],
        )

    form.widget(
        'dossier_manager',
        KeywordFieldWidget,
        async=True,
        template_selection='usersAndGroups',
        template_result='usersAndGroups',
        )

    form.write_permission(
        dossier_manager='opengever.dossier.ProtectDossier',
        )

    dossier_manager = schema.Choice(
        title=_(
            u'label_dossier_manager',
            default=u'Dossier manager',
            ),
        description=_(
            u'description_dossier_manager',
            default=(
                u'This user or group will get the dossier manager role after '
                u'protecting the dossier.'
                )
            ),
        source=AllUsersAndGroupsSourceBinder(),
        defaultFactory=current_user,
        required=False,
        missing_value=None,
        )


alsoProvides(IProtectDossier, IFormFieldProvider)


class DossierProtection(AnnotationsFactoryImpl):
    """Implement protected dossiers."""

    READING_ROLES = [
        'Reader',
        ]

    READING_AND_WRITING_ROLES = READING_ROLES + [
        'Editor',
        'Contributor',
        'Reviewer',
        'Publisher',
        ]

    DOSSIER_MANAGER_ROLES = READING_AND_WRITING_ROLES + [
        'DossierManager',
        ]

    def __init__(self, context, annotation_schema):
        super(DossierProtection, self).__init__(context, annotation_schema)
        self.context = context

    def protect(self, force_update=False):
        """Update the role-inheritance and the role-mapping of a dossier.

        The protection-proccess will be started so long as the current user
        does not have the 'Manager' role and the user also has the required
        permission to protect dossiers.

        First it checks, if the protection is activate or not. Depending on the
        protection-status, the roles will be inherited or not.

        After updating the inheritance, all the localroles will be flushed
        to continue without predefined local-roles.

        Then, all the defined users in the protection-schema will receive the
        related local-roles.

        At the end, the current editing user will receive full access to the
        to the current dossier also if it not defined in the schema. This
        is to prevent locking out yourself.
        """
        if not self.need_update(force_update):
            return

        self.update_role_inheritance()
        self.clear_local_roles()

        if self.is_dossier_protected():
            self.update_role_settings()

        self.context.reindexObjectSecurity()

    def need_update(self, force_update=False):
        """Only update the permissions if the current user has the
        protect dossier permission and a dossier manager is set.
        """
        if force_update:
            return True

        return api.user.has_permission(
            'opengever.dossier: Protect dossier', obj=self.context) and \
            self.dossier_manager

    def update_role_inheritance(self):
        old_value = self.is_role_inheritance_blocked(self.context)
        new_value = self.need_block_role_inheritance()
        if old_value == new_value:
            return

        setattr(self.context, '__ac_local_roles_block__', new_value)
        self.context.reindexObject(idxs=['blocked_local_roles'])

    def need_block_role_inheritance(self):
        return self.is_dossier_protected()

    def is_role_inheritance_blocked(self, context):
        return getattr(context, '__ac_local_roles_block__', False)

    def is_dossier_protected(self):
        return bool(self.reading or self.reading_and_writing)

    def update_role_settings(self):
        assignments = []
        for principal, roles in self.generate_role_settings().items():
            assignments.append(ProtectDossierRoleAssignment(principal, roles))

        if assignments:
            manager = RoleAssignmentManager(self.context)
            manager.reset(assignments)

    def clear_local_roles(self):
        RoleAssignmentManager(self.context).clear_all()

    def generate_role_settings(self):
        role_settings = {}

        self.extend_role_settings_for_principals(
            role_settings,
            self.reading,
            self.READING_ROLES,
            )

        self.extend_role_settings_for_principals(
            role_settings,
            self.reading_and_writing,
            self.READING_AND_WRITING_ROLES,
            )

        self.extend_role_settings_for_principals(
            role_settings,
            (self.dossier_manager, ),
            self.DOSSIER_MANAGER_ROLES,
            )

        return role_settings

    def extend_role_settings_for_principals(self, role_settings, principals, roles):  # noqa
        for principal in principals:
            role_settings[principal] = roles

    def check_local_role_consistency(self):
        """Return whether the local roles match the protection-settings.

        This happens, if you change the localroles through the sharing tab on a
        protected dossier.

        A local-role inconsistency can also occur through system
        functionalities.

        I.e. if you create a remote task in a dossier, the roles are reset by
        the system.
        """
        role_settings = self.generate_role_settings()

        for principal, roles in self.context.get_local_roles():
            # Ignore owner role
            roles = tuple(role for role in roles if role != 'Owner')

            role_setting = role_settings.get(principal)
            if not role_setting:
                # A new principal have been added to the localroles
                return False

            if set(roles).symmetric_difference(set(role_setting)):
                # The roles of a principal changed
                return False

            role_settings.pop(principal)

        if role_settings:
            # A principal have been removed from the localroles
            return False

        return True


class DossierProtectionFactory(AnnotationStorage):
    """Provide an annotation storage wrapper for protected dossiers."""

    def __call__(self, context):
        return DossierProtection(context, self.schema)


alsoProvides(DossierProtectionFactory, ISchemaAwareFactory)
