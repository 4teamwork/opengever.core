from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.base.solr.fields import to_relative_path
from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder
from opengever.sharing.security import disabled_permission_check
from plone import api
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.component import queryAdapter


def repository_number_to_outine_level(repository_number):
    # All of the current repository number formatters are dot separated
    return len(repository_number.split('.')) - 1


def bool_label(value):
    translater = StringTranslater(api.portal.get().REQUEST, 'opengever.repository').translate
    return (
        translater(_(u'label_true', default='Yes'))
        if value
        else
        translater(_(u'label_false', default='No'))
    )


def get_link(value, context):
    return context.absolute_url()


class RepositoryRootExcelExport(BrowserView):
    """Export a repository tree as an Excel document."""

    def __call__(self):
        data = generate_report(self.request, self.context)
        if not data:
            msg = StringTranslater(self.request, 'opengever.repository').translate(_(u'Could not generate the report.'))
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())
        response = self.request.RESPONSE
        response.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        set_attachment_content_disposition(self.request, "repository_report.xlsx")
        return data


def generate_report(request, context):
    # Translations from opengever.base
    base_translater = StringTranslater(request, 'opengever.base').translate
    label_classification = base_translater(u'label_classification')
    label_privacy_layer = base_translater(u'label_privacy_layer')
    label_public_trial = base_translater(u'label_public_trial')
    label_retention_period = base_translater(u'label_retention_period')
    label_retention_period_annotation = base_translater(u'label_retention_period_annotation')
    label_archival_value = base_translater(u'label_archival_value')
    label_archival_value_annotation = base_translater(u'label_archival_value_annotation')
    label_custody_period = base_translater(u'label_custody_period')

    # Translations local to opengever.repository
    repository_translater = StringTranslater(request, 'opengever.repository').translate
    label_valid_from = repository_translater(u'label_valid_from')
    label_valid_until = repository_translater(u'label_valid_until')

    # Translations defined here for opengever.repository
    label_repository_number = repository_translater(_(
        u'label_repository_number',
        default=u'Repository number',
    ))
    label_repositoryfolder_title_de = repository_translater(_(
        u'label_repositoryfolder_title_de',
        default=u'Repositoryfolder title (German)',
    ))
    label_repositoryfolder_title_fr = repository_translater(_(
        u'label_repositoryfolder_title_fr',
        default=u'Repositoryfolder title (French)',
    ))
    label_repositoryfolder_title_en = repository_translater(_(
        u'label_repositoryfolder_title_en',
        default=u'Repositoryfolder title (English)',
    ))
    label_repositoryfolder_description = repository_translater(_(
        u'label_repositoryfolder_description',
        default=u'Repositoryfolder description',
    ))
    label_blocked_inheritance = repository_translater(_(
        u'label_blocked_inheritance',
        default=u'Blocked inheritance',
    ))
    label_groupnames_with_local_reader_role = repository_translater(_(
        u'label_groupnames_with_local_reader_role',
        default=u'Read dossiers local',
    ))
    label_groupnames_with_local_contributor_role = repository_translater(_(
        u'label_groupnames_with_local_contributor_role',
        default=u'Create dossiers local',
    ))
    label_groupnames_with_local_editor_role = repository_translater(_(
        u'label_groupnames_with_local_editor_role',
        default=u'Edit dossiers local',
    ))
    label_groupnames_with_local_reviewer_role = repository_translater(_(
        u'label_groupnames_with_local_reviewer_role',
        default=u'Close dossiers local',
    ))
    label_groupnames_with_local_publisher_role = repository_translater(_(
        u'label_groupnames_with_local_publisher_role',
        default=u'Reactivate dossiers local',
    ))
    label_groupnames_with_local_manager_role = repository_translater(_(
        u'label_groupnames_with_local_manager_role',
        default=u'Manage dossiers local',
    ))
    label_groupnames_with_local_taskresponsible_role = repository_translater(_(
        u'label_groupnames_with_local_taskresponsible_role',
        default=u'Task responsible local',
    ))
    label_groupnames_with_local_or_inherited_reader_role = repository_translater(_(
        u'label_groupnames_with_local_or_inherited_reader_role',
        default=u'Read dossiers',
    ))
    label_groupnames_with_local_or_inherited_contributor_role = repository_translater(_(
        u'label_groupnames_with_local_or_inherited_contributor_role',
        default=u'Create dossiers',
    ))
    label_groupnames_with_local_or_inherited_editor_role = repository_translater(_(
        u'label_groupnames_with_local_or_inherited_editor_role',
        default=u'Edit dossiers',
    ))
    label_groupnames_with_local_or_inherited_reviewer_role = repository_translater(_(
        u'label_groupnames_with_local_or_inherited_reviewer_role',
        default=u'Close dossiers',
    ))
    label_groupnames_with_local_or_inherited_publisher_role = repository_translater(_(
        u'label_groupnames_with_local_or_inherited_publisher_role',
        default=u'Reactivate dossiers',
    ))
    label_groupnames_with_local_or_inherited_manager_role = repository_translater(_(
        u'label_groupnames_with_local_or_inherited_manager_role',
        default=u'Manage dossiers',
    ))
    label_groupnames_with_local_or_inherited_taskresponsible_role = repository_translater(_(
        u'label_groupnames_with_local_or_inherited_taskresponsible_role',
        default=u'Task responsible',
    ))

    label_repositoryfolder_uid = repository_translater(_(
        u'label_repositoryfolder_uid',
        default=u'UID',
    ))
    label_repositoryfolder_path = repository_translater(_(
        u'label_repositoryfolder_path',
        default=u'Path',
    ))

    column_map = (
        {'id': 'get_repository_number', 'title': label_repository_number, 'fold_by_method': repository_number_to_outine_level, 'callable': True},  # noqa
        {'id': 'get_folder_uid', 'title': label_repositoryfolder_uid, 'callable': True},
        {'id': 'get_folder_path', 'title': label_repositoryfolder_path, 'callable': True, 'hyperlink': get_link,},  # noqa
        {'id': 'title_de', 'title': label_repositoryfolder_title_de},
        {'id': 'title_fr', 'title': label_repositoryfolder_title_fr},
        {'id': 'title_en', 'title': label_repositoryfolder_title_en},
        {'id': 'description', 'title': label_repositoryfolder_description},
        {'id': 'classification', 'title': label_classification, 'transform': base_translater, 'default': u''},
        {'id': 'privacy_layer', 'title': label_privacy_layer, 'transform': base_translater, 'default': u''},
        {'id': 'public_trial', 'title': label_public_trial, 'transform': base_translater, 'default': u''},
        {'id': 'get_retention_period', 'title': label_retention_period, 'callable': True, 'default': u''},
        {'id': 'get_retention_period_annotation', 'title': label_retention_period_annotation, 'callable': True, 'default': u''},  # noqa
        {'id': 'get_archival_value', 'title': label_archival_value, 'transform': base_translater, 'callable': True, 'default': u''},  # noqa
        {'id': 'get_archival_value_annotation', 'title': label_archival_value_annotation, 'callable': True, 'default': u''},  # noqa
        {'id': 'get_custody_period', 'title': label_custody_period, 'callable': True, 'default': u''},
        {'id': 'valid_from', 'title': label_valid_from},
        {'id': 'valid_until', 'title': label_valid_until},
        {'id': '__ac_local_roles_block__', 'title': label_blocked_inheritance, 'transform': bool_label, 'default': False},  # noqa
        {'id': 'get_groupnames_with_local_reader_role', 'title': label_groupnames_with_local_reader_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_contributor_role', 'title': label_groupnames_with_local_contributor_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_editor_role', 'title': label_groupnames_with_local_editor_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_reviewer_role', 'title': label_groupnames_with_local_reviewer_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_publisher_role', 'title': label_groupnames_with_local_publisher_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_manager_role', 'title': label_groupnames_with_local_manager_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_taskresponsible_role', 'title': label_groupnames_with_local_taskresponsible_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_or_inherited_reader_role', 'title': label_groupnames_with_local_or_inherited_reader_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_or_inherited_contributor_role', 'title': label_groupnames_with_local_or_inherited_contributor_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_or_inherited_editor_role', 'title': label_groupnames_with_local_or_inherited_editor_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_or_inherited_reviewer_role', 'title': label_groupnames_with_local_or_inherited_reviewer_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_or_inherited_publisher_role', 'title': label_groupnames_with_local_or_inherited_publisher_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_or_inherited_manager_role', 'title': label_groupnames_with_local_or_inherited_manager_role, 'callable': True},  # noqa
        {'id': 'get_groupnames_with_local_or_inherited_taskresponsible_role', 'title': label_groupnames_with_local_or_inherited_taskresponsible_role, 'callable': True},  # noqa

    )

    # We sort these by reference number to preserve user experienced ordering
    active_formatter = api.portal.get_registry_record(name='formatter', interface=IReferenceNumberSettings)
    formatter = queryAdapter(api.portal.get(), IReferenceNumberFormatter, name=active_formatter)
    repository_brains = sorted(
        api.content.find(context, object_provides=IRepositoryFolder.__identifier__),
        key=formatter.sorter,
    )
    repository_folders = [context] + [brain.getObject() for brain in repository_brains]

    # We need to disable the permission checks to get the sharing roles
    with disabled_permission_check():
        # XXX - the excel importer expects 4 non-meaningful rows
        return XLSReporter(
            request,
            column_map,
            [RepositoryFolderWrapper(folder) for folder in repository_folders],
            sheet_title=repository_translater(u'RepositoryRoot'),
            blank_header_rows=4,
        )()


class RepositoryFolderWrapper(object):
    """Wrapper object to avoid fetching role_settings multiple times."""

    def __init__(self, repofolder):
        self._repofolder = repofolder
        self._local_roles_cache = None

    def __getattr__(self, name):
        return getattr(self._repofolder, name)

    def _fetch_role_settings(self):
        if not self._local_roles_cache:
            sharing_view = getMultiAdapter((self._repofolder, self.REQUEST), name="sharing")
            self._local_roles_cache = sharing_view.existing_role_settings()

        return self._local_roles_cache

    def get_groupnames_with_local_role(self, rolename):
        return "\n".join(set([
            group
            for group, roles in self._repofolder.get_local_roles()
            for role in roles
            if role == rolename
        ]))

    def get_groupnames_with_local_or_inherited_role(self, rolename):
        groups = []
        for role in self._fetch_role_settings():
            if role['roles'].get(rolename):
                groups.append(role.get('id'))
        return "\n".join(groups)

    def get_folder_path(self):
        """"Returns the relative path of the repository folder
        Example:
            If the physical path components are ('', 'fd', 'ordnungssystem')
            this method returns 'ordnungssystem'.
        """
        return to_relative_path('/'.join(self._repofolder.getPhysicalPath()))

    def get_folder_uid(self):
        return self._repofolder.UID()

    def get_groupnames_with_local_reader_role(self):
        return self.get_groupnames_with_local_role('Reader')

    def get_groupnames_with_local_contributor_role(self):
        return self.get_groupnames_with_local_role('Contributor')

    def get_groupnames_with_local_editor_role(self):
        return self.get_groupnames_with_local_role('Editor')

    def get_groupnames_with_local_reviewer_role(self):
        return self.get_groupnames_with_local_role('Reviewer')

    def get_groupnames_with_local_publisher_role(self):
        return self.get_groupnames_with_local_role('Publisher')

    def get_groupnames_with_local_manager_role(self):
        return self.get_groupnames_with_local_role('Manager')

    def get_groupnames_with_local_taskresponsible_role(self):
        return self.get_groupnames_with_local_role('TaskResponsible')

    def get_groupnames_with_local_or_inherited_reader_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Reader')

    def get_groupnames_with_local_or_inherited_contributor_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Contributor')

    def get_groupnames_with_local_or_inherited_editor_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Editor')

    def get_groupnames_with_local_or_inherited_reviewer_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Reviewer')

    def get_groupnames_with_local_or_inherited_publisher_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Publisher')

    def get_groupnames_with_local_or_inherited_manager_role(self):
        return self.get_groupnames_with_local_or_inherited_role('Manager')

    def get_groupnames_with_local_or_inherited_taskresponsible_role(self):
        return self.get_groupnames_with_local_or_inherited_role('TaskResponsible')
