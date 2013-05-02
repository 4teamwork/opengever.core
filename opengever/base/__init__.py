from zope.i18nmessageid import MessageFactory
import csv

_ = MessageFactory('opengever.base')

VERSION = 'GEVER Version %(version)s'


class OpenGeverCSVDialect(csv.excel):
    """A CSV dialect based on the standard Excel dialect but with support for
    escaped characters (double quotes in particular).
    """
    escapechar = '\\'


csv.register_dialect(u'OpenGeverCSV', OpenGeverCSVDialect)
