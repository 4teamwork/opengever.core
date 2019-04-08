from datetime import datetime
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile


class TestDispositionExcelExport(IntegrationTestCase):

    @browsing
    def test_label_row(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='download_excel')

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
        self.login(self.records_manager, browser)

        ILifeCycle(self.offered_dossier_to_destroy).archival_value_annotation = "In Absprache mit ARCH."
        self.offered_dossier_to_archive.public_trial = 'limited-public'

        browser.open(self.disposition, view='download_excel')

        data = browser.contents
        with NamedTemporaryFile(suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

            rows = list(workbook.active.rows)

            self.assertEquals(
                [u'Client1 1.1 / 12', u'Hannah Baufrau', datetime(2000, 1, 1, 0, 0),
                 datetime(2000, 1, 31, 0, 0), u'limited-public',
                 u'archival worthy', None, u'archival worthy'],
                [cell.value for cell in rows[1]])

            self.assertEquals(
                [u'Client1 1.1 / 13', u'Hans Baumann', datetime(2000, 1, 1, 0, 0),
                 datetime(2000, 1, 15, 0, 0), u'unchecked',
                 u'not archival worthy', u'In Absprache mit ARCH.',
                 u'not archival worthy'],
                [cell.value for cell in rows[2]])

    @browsing
    def test_file_name(self, browser):
        self.enable_languages()

        self.login(self.records_manager, browser)

        browser.open()
        browser.click_on("Deutsch")
        browser.open(self.disposition, view='download_excel')
        fname = eval(browser.headers.get(
            "content-disposition").split(";")[1].split("=")[1])
        expected = "bewertungsliste_angebot-31-8-2016.xlsx"
        self.assertEquals(expected, fname)

        browser.open()
        browser.click_on(u'Fran\xe7ais')
        browser.open(self.disposition, view='download_excel')
        fname = eval(browser.headers.get(
            "content-disposition").split(";")[1].split("=")[1])
        expected = "liste_evaluation_angebot-31-8-2016.xlsx"
        self.assertEquals(expected, fname)
