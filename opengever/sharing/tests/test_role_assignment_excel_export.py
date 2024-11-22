from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile
import os


class TestExcelRoleAssignmentReport(IntegrationTestCase):

    @browsing
    def test_raises_notfound_if_no_report_id_is_given(self, browser):
        self.login(self.administrator, browser=browser)

        url = u'{}/download-role-assignment-report'.format(
            self.portal.absolute_url())

        with browser.expect_http_error(code=404):
            browser.open(url)

    @browsing
    def test_raises_badrequest_if_report_does_not_exists(self, browser):
        self.login(self.administrator, browser=browser)

        with browser.expect_http_error(code=400):
            url = u'{}/download-role-assignment-report/not-existing'.format(
                self.portal.absolute_url())
            browser.open(url)

    @browsing
    def test_role_assignment_report(self, browser):
        self.login(self.administrator, browser=browser)

        url = u'{}/download-role-assignment-report/report_0'.format(
            self.portal.absolute_url())
        browser.open(url)

        self.assertEquals(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            browser.headers['content-type'])
        self.assertEquals(
            'attachment; filename="report_0.xlsx"',
            browser.headers['content-disposition'])

        data = browser.contents
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)
            os.remove(tmpfile.name)

        rows = list(workbook.active.rows)

        self.assertSequenceEqual(
            [[u'Title', u'Read', u'Add dossiers', u'Edit dossiers',
              u'Resolve dossiers', u'Reactivate dossiers', u'Manage dossiers',
              u'Task responsible', u'Role manager'],
             [u'Ordnungssystem', None, u'x', None, None, None, None, None, None],
             [u'Subsubdossier', u'x', None, u'x', u'x', None, None, None, None],
             [u'2. Rechnungspr\xfcfungskommission',
              None, u'x', None, None, u'x', None, None, None]],
            [[cell.value for cell in row] for row in rows])
