from Missing import Value as MissingValue
from opengever.ogds.base.actor import Actor
from openpyxl import Workbook
from openpyxl.styles import Font
from plone.api.portal import get_localized_time
from StringIO import StringIO
from zope.i18n import translate


DATE_NUMBER_FORMAT = 'DD.MM.YYYY'


def value(input_string):
    """Return unicode"""

    if not isinstance(input_string, unicode):
        input_string = input_string.decode('utf-8')
    return input_string


def readable_author(author):
    """Helper method which returns the author description,
    instead of the userid"""

    return Actor.lookup(author).get_label()


def readable_date(date):
    """Helper method to return a localized date"""
    return get_localized_time(date) if date else None


class StringTranslater(object):
    """provide the translate method as helper method
    for the given domain and request"""

    def __init__(self, request, domain):
        self.request = request
        self.domain = domain

    def translate(self, value):
        """ return the translated string"""

        if value:
            return translate(value, domain=self.domain, context=self.request)
        return None


class XLSReporter(object):
    """XLS Reporter View generates a xls-report for the given results set.
    """

    def __init__(self, request, attributes, results,
                 sheet_title=u' ', footer=u'', portrait_format=False):
        """Initalize the XLS reporter
        Arguments:
        attributes -- a list of mappings (with 'id', 'title', 'transform')
        results -- a list of objects, brains or sqlalchemy objects
        """

        self.attributes = attributes
        self.results = results
        self.request = request
        self.sheet_title = sheet_title
        self.footer = footer
        self.portrait_format = portrait_format

    def __call__(self):
        workbook = self.prepare_workbook()
        # save the Workbook-data in to a StringIO
        data = StringIO()
        workbook.save(data)
        data.seek(0)
        return data.read()

    def prepare_workbook(self):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = self.sheet_title
        sheet.oddFooter.center.text = self.footer

        self.insert_label_row(sheet)
        self.insert_value_rows(sheet)

        return workbook

    def insert_label_row(self, sheet):
        title_font = Font(bold=True)
        for i, attr in enumerate(self.attributes, 1):
            cell = sheet.cell(row=1, column=i)
            cell.value = translate(attr.get('title', ''), context=self.request)
            cell.font = title_font

    def insert_value_rows(self, sheet):
        for row, obj in enumerate(self.results, 2):
            for column, attr in enumerate(self.attributes, 1):
                cell = sheet.cell(row=row, column=column)
                value = getattr(obj, attr.get('id'))
                if attr.get('callable'):
                    value = value()
                if attr.get('transform'):
                    value = attr.get('transform')(value)
                if value == MissingValue:
                    value = ''

                cell.value = value

                if 'number_format' in attr:
                    cell.number_format = attr.get('number_format')
