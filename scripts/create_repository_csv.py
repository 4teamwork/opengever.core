# -*- coding: utf-8 -*-
"""Script to create a repository.csv (as needed by the repositors.cfg
transmogrifier config) from an Excel .xlsx file.

Usage: bin/zopepy scripts/create_repository_csv.py src/opengever.zug.foobar/ foo-bar 
"""
from os.path import basename
import csv
import importlib
import os
import sys
import xlrd


PRIVACY_LAYER_MAPPING = {u"Enthält schützenswerte Personendaten": 'privacy_layer_yes',
                         u"Keine Datenschutzstufe": 'privacy_layer_no',
}

CLASSIFICATION_MAPPING = {u"Nicht klassifiziert": 'unprotected',
                         u"Vertraulich": 'confidential',
                         u'Geheim':'classified'
}

PUBLIC_TRIAL_MAPPING = {u"Noch nicht geprüft": 'unchecked',
                         u"Öffentlich": 'public',
                         u'Nicht öffentlich':'private'
}

ARCHIVAL_VALUE_MAPPING = {u'Noch nicht geprüft': u'unchecked',
                          u'Anbieten': u'prompt',
                          u'Archivwürdig': u'archival worthy',
                          u'Nicht archivwürdig': u'not archival worthy',
                          u'Sampling': u'archival worthy with sampling',
}


# Some of the following parts are based on
# http://code.activestate.com/recipes/546518/

def xlrd_xls2array(infilename):
    """ Returns a list of sheets; each sheet is a dict containing
    * sheet_name: unicode string naming that sheet
    * sheet_data: 2-D table holding the converted cells of that sheet
    """
    book       = xlrd.open_workbook(infilename)
    sheets     = []
    formatter  = lambda(t,v): format_excelval(book,t,v,False)

    for sheet_name in book.sheet_names():
        raw_sheet = book.sheet_by_name(sheet_name)
        data      = []
        for row in range(raw_sheet.nrows):
            (types, values) = (raw_sheet.row_types(row), raw_sheet.row_values(row))
            data.append(map(formatter, zip(types, values)))
        sheets.append({ 'sheet_name': sheet_name, 'sheet_data': data })
    return sheets


def tupledate_to_isodate(tupledate):
    """
    Turns a gregorian (year, month, day, hour, minute, nearest_second) into a
    standard YYYY-MM-DDTHH:MM:SS ISO date.  If the date part is all zeros, it's
    assumed to be a time; if the time part is all zeros it's assumed to be a date;
    if all of it is zeros it's taken to be a time, specifically 00:00:00 (midnight).

    Note that datetimes of midnight will come back as date-only strings.  A date
    of month=0 and day=0 is meaningless, so that part of the coercion is safe.
    For more on the hairy nature of Excel date/times see http://www.lexicon.net/sjmachin/xlrd.html
    """
    (y,m,d, hh,mm,ss) = tupledate
    nonzero = lambda n: n!=0
    date = "%04d-%02d-%02d"  % (y,m,d)    if filter(nonzero, (y,m,d))                else ''
    time = "T%02d:%02d:%02d" % (hh,mm,ss) if filter(nonzero, (hh,mm,ss)) or not date else ''
    return date+time


def format_excelval(book, type, value, wanttupledate):
    """ Clean up the incoming excel data """
    ##  Data Type Codes:
    ##  EMPTY   0
    ##  TEXT    1 a Unicode string
    ##  NUMBER  2 float
    ##  DATE    3 float
    ##  BOOLEAN 4 int; 1 means TRUE, 0 means FALSE
    ##  ERROR   5
    #returnrow = []
    if   type == 2: # TEXT
        if value == int(value): value = int(value)
    elif type == 3: # NUMBER
        datetuple = xlrd.xldate_as_tuple(value, book.datemode)
        value = datetuple if wanttupledate else tupledate_to_isodate(datetuple)
    elif type == 5: # ERROR
        value = xlrd.error_text_from_code[value]
    return value


def utf8ize(l):
    """Make string-like things into utf-8, leave other things alone
    """
    return [unicode(s).encode("utf-8") if hasattr(s,'encode') else s for s in l]


def dump_csv(table, outdir, outfilename):
    stream = file(os.path.join(outdir, outfilename), 'wb')
    csvout = csv.writer(stream, delimiter=',', doublequote=False, escapechar='\\')
    csvout.writerows( map(utf8ize, table) )
    stream.close()


def clean_repository_table(table, client_id):
    sheet_data = table['sheet_data']
    # Drop human readable header row
    del sheet_data[0]
    # Drop empty row
    del sheet_data[0]
    # Drop empty row
    del sheet_data[1]
    for rownum, row in enumerate(sheet_data):
        for colnum, cell in enumerate(row):
            if colnum in (17, 18, 19, 20, 21) and not rownum == 0:
                # local roles
                if cell:
                    local_roles = cell.strip().replace('"', '').split(',')
                    prefixed_roles = ["og_%s_%s" % (client_id, principal.strip()) for principal in local_roles]
                    new_cell_value = ', '.join(prefixed_roles)
                    row[colnum] = new_cell_value
            for mapping in (PRIVACY_LAYER_MAPPING,
                            CLASSIFICATION_MAPPING,
                            PUBLIC_TRIAL_MAPPING,
                            ARCHIVAL_VALUE_MAPPING):
                for key, value in mapping.items():
                    if isinstance(cell, basestring) and cell.lower() == key.lower():
                        row[colnum] = value
    return table


def main():
    if len(sys.argv) < 3:
        raise Exception('Please supply path to zug package (opengever.zug/opengever/zug/foobar) and client id (foo-bar).')
    policy_path = sys.argv[1] # opengever.zug/opengever/zug/foobar
    client_id = sys.argv[2] # foo-bar

    # Strip trailing slash in order for basename to work as expected
    policy_path = policy_path.rstrip('/')    # src/opengever/zug/foobar
    bn = basename(policy_path)               # foobar
    path = os.path.join(policy_path, 'data')
    xlsx_path = os.path.join(path, 'config.xlsx')

    if not os.path.exists(xlsx_path):
        raise Exception('Could not find config.xlsx at %s.' % xlsx_path)

    dotted_name = ".".join(["opengever", "zug", bn]) # opengever.zug.foobar
    policy_module = importlib.import_module(dotted_name)

    tables = xlrd_xls2array(xlsx_path)
    repository_table = tables[1] # use 'Ordnungssystem' table
    repository_table = clean_repository_table(repository_table, client_id)

    outdir = os.path.split(xlsx_path)[0]
    dump_csv(repository_table['sheet_data'], outdir, 'repository.csv')
    print "Wrote repository.csv to %s" % outdir


if __name__ == '__main__':
    main()


