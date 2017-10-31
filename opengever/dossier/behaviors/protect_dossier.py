from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.dossier import _
from opengever.ogds.base.sources import AllUsersAndGroupsSourceBinder
from plone import api
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.annotation import AnnotationsFactoryImpl
from plone.behavior.annotation import AnnotationStorage
from plone.behavior.interfaces import ISchemaAwareFactory
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface


class IProtectDossierMarker(Interface):
    """Marker interface for the protect dossier behavior"""


class IProtectDossier(model.Schema):

    model.fieldset(
        u'protect',
        label=_(u'fieldset_protect', default=u'Protect'),
        fields=['reading',
                'reading_and_writing'],
        )

    form.widget('reading', KeywordFieldWidget, async=True)
    form.write_permission(reading='opengever.dossier.ProtectDossier')
    reading = schema.List(
        title=_(u'label_reading', default=u'Reading'),
        description=_(
            u'description_reading',
            default=u'Choose users and groups which have only readable access to the dossier'),
        value_type=schema.Choice(source=AllUsersAndGroupsSourceBinder()),
        required=False,
        missing_value=[],
        )

    form.widget('reading_and_writing', KeywordFieldWidget, async=True)
    form.write_permission(reading_and_writing='opengever.dossier.ProtectDossier')
    reading_and_writing = schema.List(
        title=_(u'label_reading_and_writing', default=u'Reading and writing'),
        description=_(
            u'description_reading_and_writing',
            default=u'Choose users and groups which have readable and writing access to the dossier'),
        value_type=schema.Choice(source=AllUsersAndGroupsSourceBinder()),
        required=False,
        missing_value=[],
        )


alsoProvides(IProtectDossier, IFormFieldProvider)


class DossierProtection(AnnotationsFactoryImpl):

    READING_ROLES = ['Reader']
    READING_AND_WRITING_ROLES = READING_ROLES + ['Editor', 'Contributor', 'Reviewer', 'Publisher']
    DOSSIER_MANAGER_ROLES = READING_AND_WRITING_ROLES + ['DossierManager']

    def __init__(self, context, schema):
        super(DossierProtection, self).__init__(context, schema)
        self.context = context

    def protect(self, force_update=False):
        """Updates the role-inheritance and the role-mapping of the current object.

        The protection-proccess will be started as soon as the user is not a manager
        and it has the required permission to protect dossiers.

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
        protect dossier permission and is not a global manager.
        """
        if force_update:
            return True

        return api.user.has_permission(
            'opengever.dossier: Protect dossier', obj=self.context) and not \
            api.user.get_current().has_role('Manager')

    def update_role_inheritance(self):
        old_value = self.is_role_inheritance_blocked(self.context)
        new_value = self.need_block_role_inheritance()
        if old_value == new_value:
            return

        setattr(self.context, '__ac_local_roles_block__', new_value)

    def need_block_role_inheritance(self):
        return self.is_dossier_protected()

    def is_role_inheritance_blocked(self, context):
        return getattr(context, '__ac_local_roles_block__', False)

    def is_dossier_protected(self):
        return bool(self.reading or self.reading_and_writing)

    def update_role_settings(self):
        for principal, roles in self.generate_role_settings():
            self.context.manage_setLocalRoles(principal, roles)

    def clear_local_roles(self):
        self.context.manage_delLocalRoles([principal for principal, roles in self.context.get_local_roles()])

    def generate_role_settings(self):
        role_settings = []

        self.extend_role_settings_for_principals(
            role_settings, self.reading, self.READING_ROLES)

        self.extend_role_settings_for_principals(
            role_settings, self.reading_and_writing, self.READING_AND_WRITING_ROLES)

        self.extend_role_settings_for_principals(
            role_settings, [api.user.get_current().getId()], self.DOSSIER_MANAGER_ROLES)

        return role_settings

    def extend_role_settings_for_principals(self, role_settings, principals, roles):
        for principal in principals:
            role_settings.append((principal, roles))


class DossierProtectionFactory(AnnotationStorage):

    def __call__(self, context):
        return DossierProtection(context, self.schema)


alsoProvides(DossierProtectionFactory, ISchemaAwareFactory)
