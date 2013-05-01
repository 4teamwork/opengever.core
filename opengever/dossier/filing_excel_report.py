# -*- coding: utf-8 -*-
from opengever.base.interfaces import ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossierMarker
from ordereddict import OrderedDict
from xlwt import Formula
from xlwt import Workbook
from zope.component import getUtility
import re
import xlwt


BASE_URL = 'https://portal.zg.ch/ktzg/opengever'

# Formatting styles
title_style = xlwt.easyxf('font: name Arial, height 280, bold on;')
header_style = xlwt.easyxf('font: name Arial, bold on;')
important_style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
error_style = xlwt.easyxf('pattern: pattern solid, fore_colour red;')
link_style = xlwt.easyxf('font: color blue, underline single;')


def sort_by_reference(brains):
    """Sorts a list of brains by their reference (Aktenzeichen).
    """
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

    def get_affected_counters(self):
        affected_counters = {}
        for checker_name, results in self.results.items():
            if not checker_name in ['check_for_counters_needing_initialization', 'check_for_bad_counters']:
                continue
            else:
                for result in results:
                    counter_key = result[0]
                    associated_fns = self.get_associated_filing_numbers(counter_key)
                    num_dossiers = len(associated_fns)
                    highest_fn = self.get_highest_filing_number(associated_fns)
                    try:
                        counter_value = self.get_counter_value(counter_key)
                    except ValueError:
                        counter_value = 0
                    error = checker_name.replace('check_for_', '')
                    affected_counters[counter_key] = {'counter_value': counter_value,
                                                      'num_dossiers': num_dossiers,
                                                      'highest_fn': highest_fn,
                                                      'errors': [error]}
        return affected_counters

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

    def get_all_counters_including_problems(self):
        all_counters = OrderedDict()
        affected_counters = self.get_affected_counters()
        counters = self.get_filing_number_counters()

        for counter_key, counter in counters.items():
            if counter_key in affected_counters.keys():
                all_counters[counter_key] = affected_counters[counter_key]
            else:
                associated_fns = self.get_associated_filing_numbers(counter_key)
                num_dossiers = len(associated_fns)
                try:
                    counter_value = self.get_counter_value(counter_key)
                except ValueError:
                    counter_value = 0
                if associated_fns:
                    highest_fn = self.get_highest_filing_number(associated_fns)
                else:
                    highest_fn = ''

                all_counters[counter_key] = {'counter_value': counter_value,
                                             'num_dossiers': num_dossiers,
                                             'highest_fn': highest_fn,
                                             'errors': []}

        all_counters.update(affected_counters)
        return all_counters

    def create_excel_report(self, filename=None):
        if not filename:
            filename = self.client_id

        workbook = Workbook()

        # General Info
        info_sheet = workbook.add_sheet("Info")
        info_sheet.write(0, 0, u"Allgemeine Informationen", title_style)

        info_sheet.write(2, 0, u"Aktuelles Mandantenpräfix", header_style)
        info_sheet.write(2, 1, self.current_client_prefix)

        info_sheet.write(4, 0, u"Duplikate", header_style)
        info_sheet.write(4, 1, len(self.results['check_for_fuzzy_duplicates']))
        info_sheet.write(5, 0, u"Altes Ablagepräfix", header_style)
        info_sheet.write(5, 1, len(self.results['check_for_legacy_filing_prefixes']))
        info_sheet.write(6, 0, u"Fehlendes Mandantenpräfix", header_style)
        info_sheet.write(6, 1, len(self.results['check_for_missing_client_prefixes']))
        info_sheet.write(7, 0, u"Mandantenpräfix mit Punkt", header_style)
        info_sheet.write(7, 1, len(self.results['check_for_dotted_client_prefixes']))

        info_sheet.write(9, 0, u"Falsche Zähler", header_style)
        info_sheet.write(9, 1, len(self.results['check_for_bad_counters']))
        info_sheet.write(10, 0, u"Zähler die initialisiert werden müssen", header_style)
        info_sheet.write(10, 1, len(self.results['check_for_counters_needing_initialization']))


        # Dossiers
        sheet = workbook.add_sheet("Ablagenummern")
        sheet.write(0, 0, u"Ablagenummern", title_style)
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(3)
        sheet.set_remove_splits(True)
        sheet.write(2, 0, u"Laufnummer", header_style)
        sheet.write(2, 1, u"Aktenzeichen", header_style)
        sheet.write(2, 2, u"Alte Ablagenr.", header_style)
        sheet.write(2, 3, u"Korrigierte Ablagenr.", header_style)
        sheet.write(2, 4, u"F1: Duplikat", header_style)
        sheet.write(2, 5, u"F2: Altes Ablagepräfix", header_style)
        sheet.write(2, 6, u"F3: Fehlendes Mandantenpräfix", header_style)
        sheet.write(2, 7, u"F4: Mandantenpräfix mit Punkt", header_style)
        sheet.write(2, 8, u"Link", header_style)
        sheet.write(2, 9, u"Pfad", header_style)

        all_dossiers = self.get_all_dossiers_including_problems()
        rownum = 3
        for path, details in all_dossiers.items():
            errors = details['errors']
            sheet.write(rownum, 0, details['sequence_number'])
            sheet.write(rownum, 1, details['reference_number'])
            if errors:
                # Has errors
                sheet.write(rownum, 2, details['filing_number'], error_style)
                sheet.write(rownum, 3, u'', important_style)
                if 'duplicates' in errors or 'fuzzy_duplicates' in errors:
                    sheet.write(rownum, 4, 'DUPLICATE')
                if 'legacy_filing_prefixes' in errors:
                    sheet.write(rownum, 5, 'LEGACY_PREFIX')
                if 'missing_client_prefixes' in errors:
                    sheet.write(rownum, 6, 'MISSING_CLIENT_PREFIX')
                if 'dotted_client_prefixes' in errors:
                    sheet.write(rownum, 7, 'DOTTED_CLIENT_PREFIX')

            else:
                # Is clean
                sheet.write(rownum, 2, details['filing_number'])
            url = "%s%s" % (BASE_URL, path)
            link = Formula(
                'HYPERLINK("%s"; "%s")' % (url, details['sequence_number']))
            sheet.write(rownum, 8, link, link_style)
            sheet.write(rownum, 9, path)
            rownum += 1

        # Counters
        counter_sheet = workbook.add_sheet(u"Zähler")
        counter_sheet.write(0, 0, u"Zähler", title_style)
        counter_sheet.set_panes_frozen(True)
        counter_sheet.set_horz_split_pos(3)
        counter_sheet.set_remove_splits(True)
        counter_sheet.write(2, 0, u"Zähler", header_style)
        counter_sheet.write(2, 1, u"Aktueller Wert", header_style)
        counter_sheet.write(2, 2, u"Anzahl Dossiers", header_style)
        counter_sheet.write(2, 3, u"Höchste Ablagenummer", header_style)
        counter_sheet.write(2, 4, u"Korrigierter Wert", header_style)
        counter_sheet.write(2, 5, u"F1: Falscher Wert", header_style)
        counter_sheet.write(2, 6, u"F2: Nicht initialisiert", header_style)

        all_counters = self.get_all_counters_including_problems()
        rownum = 3
        for counter_key, details in all_counters.items():
            errors = details['errors']
            counter_sheet.write(rownum, 0, counter_key)

            counter_sheet.write(rownum, 2, details['num_dossiers'])
            counter_sheet.write(rownum, 3, details['highest_fn'])
            if errors:
                # Has errors
                counter_sheet.write(rownum, 1, details['counter_value'], error_style)
                counter_sheet.write(rownum, 4, u'', important_style)
                if 'bad_counters' in errors:
                    counter_sheet.write(rownum, 5, 'BAD_COUNTER')
                if 'counters_needing_initialization' in errors:
                    counter_sheet.write(rownum, 6, 'NEEDS_INIT')
            else:
                # Is clean
                counter_sheet.write(rownum, 1, details['counter_value'])
            rownum += 1

        with open('%s.xls' % filename, 'w') as outfile:
            workbook.save(outfile)
