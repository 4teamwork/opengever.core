# -*- coding: utf-8 -*-
from opengever.base.interfaces import ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker
from ordereddict import OrderedDict
from xlwt import Workbook
from xlwt import XFStyle
from zope.component import getUtility
import re
import xlwt


def sort_by_reference(brains):
    splitter = re.compile('[/\., ]')

    def _sortable_data(brain):
        """ Converts the "reference" into a tuple containing integers,
        which are converted well. Sorting "10" and "2" as strings
        results in wrong order..
        """

        value = getattr(brain, 'reference', '')
        if not isinstance(value, str) and not isinstance(
            value, unicode):
            return value
        parts = []
        for part in splitter.split(value):
            part = part.strip()
            try:
                part = int(part)
            except ValueError:
                pass
            parts.append(part)
        return parts

    results = list(brains)
    results.sort(
        lambda a, b: cmp(_sortable_data(a), _sortable_data(b)))
    return results



class ExcelReportMixin(object):
    """Mixin class for FilingNumberChecker that generates an Excel report for
    all dossiers and highlights filing number errors.
    """
    def get_affected_dossiers(self):
        affected_dossiers = {}
        for key, value in self.results.items():
            if key == 'check_for_counters_needing_initialization':
                continue
            elif key == 'check_for_bad_counters':
                continue
            for result in value:
                filing_number = result[0]
                path = result[1]
                error = key.replace('check_for_', '')
                if not path in affected_dossiers.keys():
                    affected_dossiers[path] = {}
                affected_dossiers[path]['filing_number'] = filing_number
                if not 'errors' in affected_dossiers[path].keys():
                    affected_dossiers[path]['errors'] = []
                affected_dossiers[path]['errors'].append(error)
        return affected_dossiers

    def get_all_dossiers_including_problems(self):
        all_dossiers = OrderedDict()
        affected_dossiers = self.get_affected_dossiers()
        brains = self.catalog(object_provides=IDossierMarker.__identifier__,
                              sort_on='path')
        brains = sort_by_reference(brains)

        for brain in brains:
            path = brain.getPath()
            obj = brain.getObject()
            if path in affected_dossiers.keys():
                all_dossiers[path] = affected_dossiers[path]
            else:
                all_dossiers[path] = {'filing_number': self.get_filing_number(obj),
                                      'errors': []}
            sn_utility = getUtility(ISequenceNumber)
            seq_num = sn_utility.get_number(obj)
            all_dossiers[path]['sequence_number'] = seq_num
            all_dossiers[path]['reference_number'] = brain.reference
        return all_dossiers

    def get_excel_report(self):
        all_dossiers = self.get_all_dossiers_including_problems()

        workbook = Workbook()
        sheet = workbook.add_sheet(self.client_id)
        sheet.portrait = False

        important_style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
        error_style = xlwt.easyxf('pattern: pattern solid, fore_colour red;')

        header_style = XFStyle()
        header_style.font.bold = True

        sheet.write(0, 0, u"Laufnummer", header_style)
        sheet.write(0, 1, u"Aktenzeichen", header_style)
        sheet.write(0, 2, u"Alte Ablagenr.", header_style)
        sheet.write(0, 3, u"Korrigierte Ablagenr.", header_style)
        sheet.write(0, 4, u"F1: Duplikat", header_style)
        sheet.write(0, 5, u"F2: Altes Ablagepräfix", header_style)
        sheet.write(0, 6, u"F3: Fehlendes Mandantenpräfix", header_style)
        sheet.write(0, 7, u"F4: Mandantenpräfix mit Punkt", header_style)
        sheet.write(0, 8, u"Pfad", header_style)

        rownum = 0
        for path, details in all_dossiers.items():
            #errors = ', '.join([p for p in details['errors']])
            errors = details['errors']
            sheet.write(rownum + 1, 0, details['sequence_number'])
            sheet.write(rownum + 1, 1, details['reference_number'])
            if errors:
                # Has errors
                sheet.write(rownum + 1, 2, details['filing_number'], important_style)
                sheet.write(rownum + 1, 3, u'', error_style)
                if 'duplicates' in errors or 'fuzzy_duplicates' in errors:
                    sheet.write(rownum + 1, 4, 'DUPLICATE')
                if 'legacy_filing_prefixes' in errors:
                    sheet.write(rownum + 1, 5, 'LEGACY_PREFIX')
                if 'missing_client_prefixes' in errors:
                    sheet.write(rownum + 1, 6, 'MISSING_CLIENT_PREFIX')
                if 'dotted_client_prefixes' in errors:
                    sheet.write(rownum + 1, 7, 'DOTTED_CLIENT_PREFIX')

            else:
                # Is clean
                sheet.write(rownum + 1, 2, details['filing_number'])
            sheet.write(rownum + 1, 8, path)
            rownum += 1
        outfile = open('%s.xls' % self.client_id, 'w')
        workbook.save(outfile)
        outfile.close()