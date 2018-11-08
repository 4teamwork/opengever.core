from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder
from plone import api
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
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
    label_repositoryfolder_description = repository_translater(_(
        u'label_repositoryfolder_description',
        default=u'Repositoryfolder description',
        ))
    label_blocked_inheritance = repository_translater(_(
        u'label_blocked_inheritance',
        default=u'Blocked inheritance',
        ))
    label_groupnames_with_reader_role = repository_translater(_(
        u'label_groupnames_with_reader_role',
        default=u'Read dossiers',
        ))
    label_groupnames_with_contributor_role = repository_translater(_(
        u'label_groupnames_with_contributor_role',
        default=u'Create dossiers',
        ))
    label_groupnames_with_editor_role = repository_translater(_(
        u'label_groupnames_with_editor_role',
        default=u'Edit dossiers',
        ))
    label_groupnames_with_reviewer_role = repository_translater(_(
        u'label_groupnames_with_reviewer_role',
        default=u'Close dossiers',
        ))
    label_groupnames_with_publisher_role = repository_translater(_(
        u'label_groupnames_with_publisher_role',
        default=u'Reactivate dossiers',
        ))
    label_groupnames_with_manager_role = repository_translater(_(
        u'label_groupnames_with_manager_role',
        default=u'Manage dossiers',
        ))

    column_map = (
        {'id': 'get_repository_number', 'title': label_repository_number, 'fold_by_method': repository_number_to_outine_level, 'callable': True},  # noqa
        {'id': 'title_de', 'title': label_repositoryfolder_title_de},
        {'id': 'title_fr', 'title': label_repositoryfolder_title_fr},
        {'id': 'description', 'title': label_repositoryfolder_description},
        {'id': 'classification', 'title': label_classification, 'transform': base_translater, 'default': u''},
        {'id': 'privacy_layer', 'title': label_privacy_layer, 'transform': base_translater, 'default': u''},
        {'id': 'public_trial', 'title': label_public_trial, 'transform': base_translater, 'default': u''},
        {'id': 'get_retention_period', 'title': label_retention_period, 'callable': True, 'default': u''},
        {'id': 'get_retention_period_annotation', 'title': label_retention_period_annotation, 'callable': True, 'default': u''},  # noqa
        {'id': 'get_archival_value', 'title': label_archival_value, 'transform': base_translater, 'callable': True, 'default': u''},  # noqa
        {'id': 'get_archival_value_annotation', 'title': label_archival_value_annotation, 'callable': True, 'default': u''},
        {'id': 'get_custody_period', 'title': label_custody_period, 'callable': True, 'default': u''},
        {'id': 'valid_from', 'title': label_valid_from},
        {'id': 'valid_until', 'title': label_valid_until},
        {'id': '__ac_local_roles_block__', 'title': label_blocked_inheritance, 'transform': bool_label, 'default': False},
        {'id': 'get_groupnames_with_reader_role', 'title': label_groupnames_with_reader_role, 'callable': True},
        {'id': 'get_groupnames_with_contributor_role', 'title': label_groupnames_with_contributor_role, 'callable': True},
        {'id': 'get_groupnames_with_editor_role', 'title': label_groupnames_with_editor_role, 'callable': True},
        {'id': 'get_groupnames_with_reviewer_role', 'title': label_groupnames_with_reviewer_role, 'callable': True},
        {'id': 'get_groupnames_with_publisher_role', 'title': label_groupnames_with_publisher_role, 'callable': True},
        {'id': 'get_groupnames_with_manager_role', 'title': label_groupnames_with_manager_role, 'callable': True},
        )

    # We sort these by reference number to preserve user experienced ordering
    active_formatter = api.portal.get_registry_record(name='formatter', interface=IReferenceNumberSettings)
    formatter = queryAdapter(api.portal.get(), IReferenceNumberFormatter, name=active_formatter)
    repository_brains = sorted(
        api.content.find(context, object_provides=IRepositoryFolder.__identifier__),
        key=formatter.sorter,
    )
    repository_folders = [context] + [brain.getObject() for brain in repository_brains]

    # XXX - the excel importer expects 4 non-meaningful rows
    return XLSReporter(
        request,
        column_map,
        repository_folders,
        sheet_title=repository_translater(u'RepositoryRoot'),
        blank_header_rows=4,
        )()
