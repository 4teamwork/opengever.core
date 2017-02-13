from collections import OrderedDict
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.bundle.loader import BUNDLE_JSON_TYPES
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
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

    def __call__(self):
        data = {}
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
            data[portal_type] = []
            log.info("Collecting %s" % portal_type)

            brains = catalog.unrestrictedSearchResults(
                portal_type=portal_type, path=root_paths)
            for brain in brains:
                obj = brain.getObject()
                guid = IAnnotations(obj).get(BUNDLE_GUID_KEY)
                if guid not in self.bundle.item_by_guid:
                    # Skip object, not part of current import
                    continue
                item_info = self.get_item_info(brain, guid)
                data[portal_type].append(item_info)

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

    def get_item_info(self, brain, guid):
        obj = brain.getObject()
        path = '/'.join(obj.getPhysicalPath())
        title = self.get_title(obj)

        item_info = OrderedDict(
            [('guid', guid), ('path', path), ('title', title)])

        file_field = self.get_file_field(obj)
        if file_field:
            item_info['file_size'] = file_field.getSize()

        return item_info


class ASCIISummaryBuilder(object):
    """Build a quick ASCII summary of object counts based on report data.
    """

    def __init__(self, report_data):
        self.report_data = report_data

    def build(self):
        report = []
        report.append('Imported objects:')
        report.append('=================')

        for portal_type, items in self.report_data.items():
            line = "%s: %s" % (portal_type, len(items))
            report.append(line)

        return '\n'.join(report)


class XLSXReportBuilder(object):
    """Build a detailed report in XLSX format based on report data.
    """

    def __init__(self, report_data):
        self.report_data = {}
        self.report_data.update(report_data)

        # Include mails in documents by moving them over
        docs = self.report_data.get('opengever.document.document', [])
        mails = self.report_data.get('ftw.mail.mail', [])
        self.report_data['opengever.document.document'] = docs + mails
        self.report_data.pop('ftw.mail.mail', None)

    def build_and_save(self, report_path):
        workbook = self.build_report()
        self.save_report(workbook, report_path)

    def save_report(self, workbook, path):
        with open(path, 'w') as report_xlsx:
            workbook.save(report_xlsx)
            log.info("Wrote report to %s" % path)
        return path

    def _write_row(self, sheet, rownum, values, bold=False):
        for col_num, value in enumerate(values, 1):
            cell = sheet.cell(row=rownum + 1, column=col_num)
            cell.value = value
            if bold:
                cell.font = Font(bold=True)

    def build_report(self):
        workbook = Workbook()
        workbook.remove_sheet(workbook.active)

        for json_name, portal_type in BUNDLE_JSON_TYPES.items():
            short_name = json_name.replace('.json', '')
            log.info("Creating sheet %s" % short_name)
            sheet = workbook.create_sheet(short_name)
            sheet.title = short_name

            # Label Row
            self._write_row(
                sheet, 0, self.report_data[portal_type][0].keys(), bold=True)

            # Data rows
            for rownum, info in enumerate(self.report_data[portal_type], 1):
                self._write_row(sheet, rownum, info.values())

        return workbook
