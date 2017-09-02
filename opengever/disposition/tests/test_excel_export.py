from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile


class TestDispositionExcelExport(FunctionalTestCase):

    def setUp(self):
        super(TestDispositionExcelExport, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository)
                               .having(title=u'Dossier A',
                                       start=date(2016, 1, 19),
                                       end=date(2016, 3, 19),
                                       public_trial='limited-public',
                                       archival_value='archival worthy'))

        self.dossier2 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository)
                               .having(title=u'Dossier B',
                                       start=date(2015, 1, 19),
                                       end=date(2015, 3, 19),
                                       public_trial='limited-public',
                                       archival_value='not archival worthy',
                                       archival_value_annotation=u'In Absprache mit ARCH.'))

        self.grant('Records Manager')
        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[self.dossier1, self.dossier2]))

    @browsing
    def test_label_row(self, browser):
        browser.login().open(self.disposition, view='download_excel')

        data = browser.contents
        with NamedTemporaryFile(suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

            self.assertEquals(
                [u'Reference Number', u'title', u'Opening Date',
                 u'Closing Date', u'Public Trial', u'Archival value',
                 u'archivalValueAnnotation', u'Appraisal'],
                [cell.value for cell in list(workbook.active.rows)[0]])
            self.assertTrue(workbook.active['A1'].font.bold)

    @browsing
    def test_value_rows(self, browser):
        browser.login().open(self.disposition, view='download_excel')

        data = browser.contents
        with NamedTemporaryFile(suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

            rows = list(workbook.active.rows)

            self.assertEquals(
                [u'Client1 1 / 1', u'Dossier A', datetime(2016, 1, 19, 0, 0),
                 datetime(2016, 3, 19, 0, 0), u'limited-public',
                 u'archival worthy', None, u'archival worthy'],
                [cell.value for cell in rows[1]])

            self.assertEquals(
                [u'Client1 1 / 2', u'Dossier B', datetime(2015, 1, 19, 0, 0),
                 datetime(2015, 3, 19, 0, 0), u'limited-public',
                 u'not archival worthy', u'In Absprache mit ARCH.',
                 u'not archival worthy'],
                [cell.value for cell in rows[2]])
