# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import resolvePackageReferenceOrFile
from zope.interface import classProvides
from zope.interface import implements
import os
import xlrd


PRIVACY_LAYER_MAPPING = {u"Enthält schützenswerte Personendaten":
                         'privacy_layer_yes',
                         u"Keine Datenschutzstufe": 'privacy_layer_no',
                         }

CLASSIFICATION_MAPPING = {u"Nicht klassifiziert": 'unprotected',
                          u"Vertraulich": 'confidential',
                          u'Geheim': 'classified'
                          }

PUBLIC_TRIAL_MAPPING = {u"Nicht geprüft": 'unchecked',
                        u"Noch nicht geprüft": 'unchecked',
                        u"Öffentlich": 'public',
                        u'Nicht öffentlich': 'private'
                        }

ARCHIVAL_VALUE_MAPPING = {u'Nicht geprüft': u'unchecked',
                          u"Noch nicht geprüft": u'unchecked',
                          u'Anbieten': u'prompt',
                          u'Archivwürdig': u'archival worthy',
                          u'Archivieren': u'archival worthy',
                          u'Nicht archivwürdig': u'not archival worthy',
                          u'Sampling': u'archival worthy with sampling',
                          u'Auswahl archivw\xfcrdig': u'archival worthy with sampling',
                          }

BLOCK_INHERITANCE_MAPPING = {u'ja': True,
                             u'nein': False}

MAPPED_FIELDS = {'archival_value': ARCHIVAL_VALUE_MAPPING,
                 'classification': CLASSIFICATION_MAPPING,
                 'privacy_layer': PRIVACY_LAYER_MAPPING,
                 'public_trial': PUBLIC_TRIAL_MAPPING,
                 'block_inheritance': BLOCK_INHERITANCE_MAPPING
                 }


class XlsSource(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.options = options

        self.path = resolvePackageReferenceOrFile(options['directory'])
        if self.path is None or not os.path.isdir(self.path):
            raise IOError('Directory does not exists: {}'.format(self.path))

    def __iter__(self):
        for item in self.previous:
            yield item

        files = sorted(os.listdir(self.path))
        for repo_num, filename in enumerate(reversed(files)):
            if not self.is_parsable(filename):
                continue

            xls_path = os.path.join(self.path, filename)
            if not os.path.isfile(xls_path):
                continue

            locals()['__traceback_info__'] = xls_path
            repository_id, extension = os.path.splitext(filename)

            keys, sheet_data = self.read_excel_file(xls_path)
            for rownum, row in enumerate(sheet_data):
                yield self.process_row(row, rownum, keys, repository_id)

    def is_parsable(self, filename):
        """Return wheter we should attempt to parse the file based on its
        filename.

        Microsoft office crates temp files in the same directory and prefixes
        them with a tilde.
        """
        if filename.startswith('.') or filename.startswith('~'):
            return False
        if not filename.endswith('.xlsx'):
            return False

        return True

    def read_excel_file(self, xls_path):
        tables = xlrd_xls2array(xls_path)
        repository_table = tables[0]
        sheet_data = repository_table['sheet_data']

        # clean up table
        sheet_data = sheet_data[4:]  # remove human readable stuff
        keys = sheet_data[0]
        del sheet_data[0]
        return keys, sheet_data

    def process_row(self, row, rownum, keys, repository_id):
        data = {}
        # repofolder or reporoot
        if rownum == 0:
            data['_type'] = u'opengever.repository.repositoryroot'
        else:
            data['_type'] = u'opengever.repository.repositoryfolder'
        data['_repo_root_id'] = repository_id

        for colnum, cell in enumerate(row):
            key = keys[colnum]

            if key in (None, '', u''):
                continue

            if key in ('classification',
                       'privacy_layer',
                       'public_trial',
                       'retention_period',
                       'custody_period',
                       'archival_value',
                       'block_inheritance',
                       ) and cell in (None, '', u''):
                continue

            if key == 'reference_number' and not isinstance(cell, basestring):
                raise Exception("Reference number has to be string: %s" % cell)

            if key in ('valid_from', 'valid_until') and cell in ('', u''):
                cell = None

            if key == 'addable_dossier_types':
                cell = cell.replace(' ', '').split(',')
                cell = [t for t in cell if not t == '']

            if key in MAPPED_FIELDS.keys():
                mapping = MAPPED_FIELDS[key]

                # Data not already a valid term
                if cell not in mapping.values():
                    cell = mapping[cell]

            data[key] = cell

        return data


# Some of the following parts are based on
# http://code.activestate.com/recipes/546518/
def xlrd_xls2array(path):
    """ Returns a list of sheets; each sheet is a dict containing
    * sheet_name: unicode string naming that sheet
    * sheet_data: 2-D table holding the converted cells of that sheet
    """
    book = xlrd.open_workbook(path)
    sheets = []

    for sheet_name in book.sheet_names():
        raw_sheet = book.sheet_by_name(sheet_name)
        data = []
        for row in range(raw_sheet.nrows):
            (types, values) = (raw_sheet.row_types(row),
                               raw_sheet.row_values(row))
            data.append(map(lambda (t, v): format_excelval(book, t, v, False),
                        zip(types, values)))
        sheets.append({'sheet_name': sheet_name, 'sheet_data': data})
    return sheets


def tupledate_to_isodate(tupledate):
    """
    Turns a gregorian (year, month, day, hour, minute, nearest_second)
    into a standard YYYY-MM-DDTHH:MM:SS ISO date.  If the date part is
    all zeros, it's assumed to be a time; if the time part is all zeros
    it's assumed to be a date; if all of it is zeros it's taken to be a
    time, specifically 00:00:00 (midnight).

    Note that datetimes of midnight will come back as date-only strings.
    A date of month=0 and day=0 is meaningless, so that part of the
    coercion is safe.
    For more on the hairy nature of Excel date/times see
    http://www.lexicon.net/sjmachin/xlrd.html
    """
    (y, m, d, hh, mm, ss) = tupledate

    def nonzero(n):
        return n != 0

    date = "%04d-%02d-%02d" % (y, m, d) if filter(nonzero,
                                                  (y, m, d)) else ''
    time = "T%02d:%02d:%02d" % (hh, mm, ss) if filter(nonzero, (hh, mm, ss)) or not date else ''
    return date + time


def format_excelval(book, type, value, wanttupledate):
    """ Clean up the incoming excel data

    Data Type Codes:
    EMPTY   0
    TEXT    1 a Unicode string
    NUMBER  2 float
    DATE    3 float
    BOOLEAN 4 int; 1 means TRUE, 0 means FALSE
    ERROR   5

    """
    if type == 2:  # TEXT
        if value == int(value):
            value = int(value)
    elif type == 3:  # NUMBER
        datetuple = xlrd.xldate_as_tuple(value, book.datemode)
        value = datetuple if wanttupledate else tupledate_to_isodate(datetuple)
    elif type == 5:  # ERROR
        value = xlrd.error_text_from_code[value]
    return value
