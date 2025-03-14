from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.role_assignments import ASSIGNMENT_VIA_DOSSIER_RESPONSIBLE
from opengever.base.role_assignments import ASSIGNMENT_VIA_PROTECT_DOSSIER
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import DossierResponsibleRoleAssignment
from opengever.base.role_assignments import ProtectDossierRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.dossier import _
from opengever.dossier import is_grant_dossier_manager_to_responsible_enabled
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.sources import AllUsersAndGroupsSourceBinder
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.annotation import AnnotationsFactoryImpl
from plone.behavior.annotation import AnnotationStorage
from plone.behavior.interfaces import ISchemaAwareFactory
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant


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
        required=False,
        missing_value=None,
    )

    @invariant
    def dossier_manager_filled_if_protection(self):
        if ((self.reading_and_writing or self.reading)
                and not self.dossier_manager):
            raise Invalid(_("A dossier manager must be selected "
                            " when protecting a dossier"))


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
        self.auto_assign_responsible = is_grant_dossier_manager_to_responsible_enabled()

    def protect(self):
        """Update the role-inheritance and the role-mapping of a dossier.

        The default implementation flushes all the local roles and then
         assigns all the defined users in the protection-schema with the
         related local-roles.

        If the auto_assign_responsible feature ist active, the function will
        always override the current dossier_manager with the current dossier
        responsible before assigning the new local roles.
        """
        self.clear_local_roles()
        self.update_role_inheritance()

        if self.auto_assign_responsible:
            self.dossier_manager = IDossier(self.context).responsible

        self.grant_dossier_manager_roles()
        self.grant_reader_and_writer_roles()

        self.context.reindexObjectSecurity()

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

    def grant_reader_and_writer_roles(self):
        manager = RoleAssignmentManager(self.context)
        assignments = {}

        for principal in self.reading:
            assignments[principal] = ProtectDossierRoleAssignment(
                principal, self.READING_ROLES)

        for principal in self.reading_and_writing:
            assignments[principal] = ProtectDossierRoleAssignment(
                principal, self.READING_AND_WRITING_ROLES)

        if assignments:
            manager.add_or_update_assignments(assignments.values())

    def grant_dossier_manager_roles(self):
        if not self.dossier_manager:
            return

        manager = RoleAssignmentManager(self.context)

        # Always set the dossier manager if the auto assign feature is enabled.
        if self.auto_assign_responsible:
            assignment = DossierResponsibleRoleAssignment(self.dossier_manager,
                                                          self.DOSSIER_MANAGER_ROLES,
                                                          self.context)
            manager.add_or_update_assignments((assignment, ))

        # Otherwise only assign it if the dossier is meant to be protected
        elif self.is_dossier_protected:
            assignment = ProtectDossierRoleAssignment(self.dossier_manager,
                                                      self.DOSSIER_MANAGER_ROLES,
                                                      self.context)
            manager.add_or_update_assignments((assignment, ))

    def clear_local_roles(self):
        manager = RoleAssignmentManager(self.context)
        manager.clear_by_causes(
            [ASSIGNMENT_VIA_SHARING,
             ASSIGNMENT_VIA_PROTECT_DOSSIER,
             ASSIGNMENT_VIA_DOSSIER_RESPONSIBLE])

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
