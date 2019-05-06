from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile


class TestDocumentReporter(IntegrationTestCase):

    @browsing
    def test_empty_document_report(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(view='document_report', data={'paths:list': []})

        self.assertEquals('Error You have not selected any Items',
                          browser.css('.portalMessage.error').text[0])

    @browsing
    def test_document_report(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            view='document_report',
            data=self.make_path_param(self.document, self.mail_eml))

        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(browser.contents)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        # One title row and two data rows
        self.assertEquals(3, len(list(workbook.active.rows)))

        self.assertSequenceEqual(
            [u'Client1 1.1 / 1 / 14',
             14L,
             u'Vertr\xe4gsentwurf',
             u'test-user (test_user_1_)',
             u'Jan 03, 2010',
             u'Jan 03, 2010',
             u'Jan 03, 2010',
             None,
             u'unchecked',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            [cell.value for cell in list(workbook.active.rows)[1]])

        self.assertSequenceEqual(
            [u'Client1 1.1 / 1 / 29',
             29L,
             u'Die B\xfcrgschaft',
             u'Freddy H\xf6lderlin <from@example.org>',
             u'Jan 01, 1999',
             u'Aug 31, 2016',
             None,
             None,
             u'unchecked',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            [cell.value for cell in list(workbook.active.rows)[2]])
