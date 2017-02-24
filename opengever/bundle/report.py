from Acquisition import aq_parent
from collections import OrderedDict
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import IReferenceNumber
from opengever.bundle.loader import BUNDLE_JSON_TYPES
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
from opengever.bundle.sections.map_local_roles import NAME_ROLE_MAPPING
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.utils import get_current_admin_unit
from openpyxl import Workbook
from openpyxl.styles import Font
from plone import api
from zope.annotation import IAnnotations
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class DataCollector(object):
    """Collect report data from Plone.
    """

    def __init__(self, bundle):
        self.bundle = bundle
        self.au_abbreviation = get_current_admin_unit().abbreviation

    def __call__(self):
        data = {'metadata': {}, 'permissions': {}}
        catalog = api.portal.get_tool('portal_catalog')

        portal_types = BUNDLE_JSON_TYPES.values()
        portal_types.append('ftw.mail.mail')

        # Determine paths of repository roots that were part of the current
        # import to limit catalog search accordingly
        portal = api.portal.get()
        root_paths = [
            '/'.join(portal.getPhysicalPath() + (r['_path'], ))
            for r in self.bundle.get_repository_roots()]

        for portal_type in portal_types:
            data['metadata'][portal_type] = []
            data['permissions'][portal_type] = []
            log.info("Collecting %s" % portal_type)

            brains = catalog.unrestrictedSearchResults(
                portal_type=portal_type, path=root_paths)

            for brain in brains:
                obj = brain.getObject()
                guid = IAnnotations(obj).get(BUNDLE_GUID_KEY)
                if guid not in self.bundle.item_by_guid:
                    # Skip object, not part of current import
                    continue
                item_info = self.get_item_metadata(obj, guid)
                data['metadata'][portal_type].append(item_info)

                if portal_type not in (
                        'opengever.document.document', 'ftw.mail.mail'):
                    permission_info = self.get_permissions(obj, guid)
                    if permission_info:
                        data['permissions'][portal_type].extend(
                            permission_info)

        return data

    def get_file_field(self, obj):
        if obj.portal_type == 'opengever.document.document':
            file_field = obj.file
        elif obj.portal_type == 'ftw.mail.mail':
            file_field = obj.message
        else:
            file_field = None

        return file_field

    def get_title(self, obj):
        if ITranslatedTitleSupport.providedBy(obj):
            return ITranslatedTitle(obj).title_de
        return obj.title

    def get_reference_number(self, obj):
        reference_adapter = IReferenceNumber(obj)
        refnum = reference_adapter.get_number()
        # Strip AdminUnit abbreviation
        refnum = refnum.replace(self.au_abbreviation, '').strip()
        return refnum

    def get_item_metadata(self, obj, guid):
        path = '/'.join(obj.getPhysicalPath())
        title = self.get_title(obj)
        parent = aq_parent(obj)
        parent_guid = IAnnotations(parent).get(BUNDLE_GUID_KEY)

        if obj.portal_type == 'opengever.repository.repositoryfolder':
            item_info = OrderedDict([
                ('guid', guid),
                ('parent_guid', parent_guid),
                ('path', path),
                ('title', title),
                ('description', obj.description),
                ('full_reference_number', self.get_reference_number(obj)),
            ])
        elif obj.portal_type == 'opengever.dossier.businesscasedossier':
            item_info = OrderedDict([
                ('guid', guid),
                ('parent_guid', parent_guid),
                ('path', path),
                ('title', title),
                ('full_reference_number', self.get_reference_number(obj)),
                ('reference_number', IDossier(obj).reference_number),
                ('responsible', IDossier(obj).responsible),
                ('description', IOpenGeverBase(obj).description),
                ('start', IDossier(obj).start),
                ('end', IDossier(obj).end),
                ('review_state', api.content.get_state(obj)),
            ])
        elif obj.portal_type in (
                'opengever.document.document', 'ftw.mail.mail'):
            file_field = self.get_file_field(obj)
            file_size = None
            file_name = None
            if file_field is not None:
                file_size = file_field.getSize()
                file_name = file_field.filename

            item_info = OrderedDict([
                ('guid', guid),
                ('parent_guid', parent_guid),
                ('path', path),
                ('title', title),
                ('file_size', file_size),
                ('file_name', file_name),
                ('document_date', obj.document_date),
            ])
        else:
            item_info = OrderedDict([
                ('guid', guid),
                ('path', path),
                ('title', title),
            ])

        return item_info

    def get_permissions(self, obj, guid):
        local_roles = obj.get_local_roles()
        inheritance_blocked = getattr(obj, '__ac_local_roles_block__', False)

        # Always include at least one row per object with the info whether
        # or not inheritance is blocked
        inheritance_blocked_row = OrderedDict([
            ('guid', guid),
            ('principal', None),
            ('read', None),
            ('edit', None),
            ('add', None),
            ('close', None),
            ('reactivate', None),
            ('blocked_inheritance', inheritance_blocked),
        ])

        # If local role assignments are present, include them as additional
        # rows (using GUID as key), one row per principal and their roles
        principal_role_rows = []
        for principal, roles in dict(local_roles).items():
            principal_roles = OrderedDict([
                ('guid', guid),
                ('principal', principal),
                ('read', False),
                ('edit', False),
                ('add', False),
                ('close', False),
                ('reactivate', False),
                ('blocked_inheritance', None),
            ])
            for rolename in roles:
                if rolename == 'Owner':
                    continue
                short_role_name = NAME_ROLE_MAPPING[rolename]
                assert short_role_name in principal_roles
                principal_roles[short_role_name] = True
            principal_role_rows.append(principal_roles)

        return [inheritance_blocked_row] + principal_role_rows


class ASCIISummaryBuilder(object):
    """Build a quick ASCII summary of object counts based on report data.
    """

    def __init__(self, report_data):
        self.report_data = report_data

    def build(self):
        report = []
        report.append('Imported objects:')
        report.append('=================')

        for portal_type, items in self.report_data['metadata'].items():
            line = "%s: %s" % (portal_type, len(items))
            report.append(line)

        return '\n'.join(report)


class XLSXReportBuilderBase(object):
    """Base class for XLSX report builders.
    """

    def __init__(self, *args, **kwargs):
        self.workbook = Workbook()
        self.workbook.remove_sheet(self.workbook.active)

    def build_and_save(self, report_path):
        self.write_report_data()
        self.save_report(report_path)

    def save_report(self, path):
        with open(path, 'w') as report_xlsx:
            self.workbook.save(report_xlsx)
            log.info("Wrote report to %s" % path)
        return path

    def add_sheet(self, sheet_name):
        log.info("Creating sheet %s" % sheet_name)
        sheet = self.workbook.create_sheet(sheet_name)
        sheet.title = sheet_name
        return sheet

    def write_row(self, sheet, rownum, values, bold=False):
        for col_num, value in enumerate(values, 1):
            cell = sheet.cell(row=rownum + 1, column=col_num)
            cell.value = value
            if bold:
                cell.font = Font(bold=True)

    def write_report_data(self):
        raise NotImplementedError("To be implemented by subclasses")


class XLSXMainReportBuilder(XLSXReportBuilderBase):
    """Build a detailed report in XLSX format based on report data.
    """

    def __init__(self, report_data):
        super(XLSXMainReportBuilder, self).__init__()
        self.report_data = {'metadata': {}, 'permissions': {}}
        metadata = self.report_data['metadata']
        metadata.update(report_data['metadata'])
        permissions = self.report_data['permissions']
        permissions.update(report_data['permissions'])
        self.metadata = metadata
        self.permissions = permissions

        # Include mails in documents by moving them over
        docs = metadata.get('opengever.document.document', [])
        mails = metadata.get('ftw.mail.mail', [])
        metadata['opengever.document.document'] = docs + mails
        metadata.pop('ftw.mail.mail', None)

        docs = permissions.get('opengever.document.document', [])
        mails = permissions.get('ftw.mail.mail', [])
        permissions['opengever.document.document'] = docs + mails
        permissions.pop('ftw.mail.mail', None)

    def _write_metadata(self):
        for json_name, portal_type in BUNDLE_JSON_TYPES.items():
            short_name = json_name.replace('.json', '')
            sheet = self.add_sheet(short_name)

            # Label Row
            self.write_row(
                sheet, 0, self.metadata[portal_type][0].keys(), bold=True)

            # Data rows
            for rownum, info in enumerate(self.metadata[portal_type], 1):
                self.write_row(sheet, rownum, info.values())

    def _write_permissions(self):
        for json_name, portal_type in BUNDLE_JSON_TYPES.items():
            if not self.permissions.get(portal_type):
                continue

            sheet_name = '%s_permissions' % json_name.replace('.json', '')
            sheet = self.add_sheet(sheet_name)

            # Label Row
            headers = self.permissions[portal_type][0].keys()
            self.write_row(sheet, 0, headers, bold=True)

            # Data rows
            permission_infos = self.permissions[portal_type]
            for rownum, perm_info in enumerate(permission_infos, 1):
                self.write_row(sheet, rownum, perm_info.values())

    def write_report_data(self):
        self._write_metadata()
        self._write_permissions()


class XLSXValidationReportBuilder(XLSXReportBuilderBase):
    """Build a validation report in XLSX format based on `errors` dictionary.
    """

    ERROR_FIELDS = OrderedDict([
        ('files_not_found', ('guid', 'filepath', 'ogg_path')),
        ('files_io_errors', ('guid', 'filepath', 'ioerror', 'ogg_path')),
        ('files_unresolvable_path', ('guid', 'filepath', 'ogg_path')),
        ('files_invalid_types', ('guid', 'filepath', 'ogg_path')),
        ('unmapped_unc_mounts', ('mount', )),
    ])

    def __init__(self, errors):
        super(XLSXValidationReportBuilder, self).__init__()
        self.errors = errors

    def write_summary(self):
        """Write a summary with counts for every message type.
        """
        sheet_name = 'summary'
        sheet = self.add_sheet(sheet_name)

        for rownum, item in enumerate(self.errors.items()):
            error_type, error_list = item
            self.write_row(sheet, rownum, (error_type, len(error_list)))

    def write_msg_sheets(self, msg_dict, field_defs):
        """Write a sheet for every message type in msg_dict.
        """
        for msg_type, msg_list in msg_dict.items():
            try:
                fields = field_defs[msg_type]
            except KeyError:
                log.warn('Unknown message type %r, skipping.' % msg_type)
                continue

            sheet = self.add_sheet(msg_type)

            # Label Row
            self.write_row(sheet, 0, fields, bold=True)

            # Data rows
            for rownum, msg in enumerate(msg_list, 1):
                self.write_row(sheet, rownum, msg)

    def write_report_data(self):
        self.write_summary()
        self.write_msg_sheets(self.errors, self.ERROR_FIELDS)
