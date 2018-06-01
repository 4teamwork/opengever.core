from opengever.base import _
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile
from zope.i18n.tests.test_itranslationdomain import Environment


class ReporterTestingMixin(object):
    def get_workbook(self, data):
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)
        return workbook


class TestReporter(IntegrationTestCase, ReporterTestingMixin):
    def test_label_row_is_translated_attribute_titles(self):
        columns = ({'id': 'title', 'title': _('label_title', default='Title')}, )
        self.login(self.regular_user)
        reporter = XLSReporter(self.request, columns, (self.document, ))
        workbook = self.get_workbook(reporter())
        self.assertEquals([u'Title'], [cell.value for cell in list(workbook.active.rows)[0]])

    def test_excel_reporter_value_rows(self):
        translation_request = Environment(('de', 'ch'))
        base_translater = StringTranslater(translation_request, 'opengever.base').translate
        columns = (
            {'id': 'title', 'title': _('label_title', default='Title')},
            {'id': 'classification', 'title': u'fooclass', 'transform': base_translater},
            {'id': 'Title', 'title': u'footitle', 'callable': True},
            )
        self.login(self.regular_user)
        reporter = XLSReporter(self.request, columns, (self.document, ))
        workbook = self.get_workbook(reporter())
        expected_row = [u'Vertr\xe4gsentwurf', u'Nicht klassifiziert', u'Vertr\xe4gsentwurf']
        self.assertEquals(expected_row, [cell.value for cell in list(workbook.active.rows)[-1]])

    def test_set_sheet_title_for_active_workbook_sheet(self):
        title = 'Aufgaben\xc3\xbcbersicht'.decode('utf-8')
        reporter = XLSReporter(None, (), (), sheet_title=title)
        workbook = self.get_workbook(reporter())
        self.assertEquals(title, workbook.active.title)
