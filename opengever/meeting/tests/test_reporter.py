from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile


class TestProposalReporter(IntegrationTestCase):

    @browsing
    def test_empty_proposal_report(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(view='proposal_report', data={'paths:list': []})

        self.assertEquals('Error You have not selected any items.',
                          browser.css('.portalMessage.error').text[0])

    @browsing
    def test_proposal_report(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            view='proposal_report',
            data=self.make_path_param(self.proposal, self.draft_proposal))

        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(browser.contents)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        # One title row and two data rows
        self.assertEquals(3, len(list(workbook.active.rows)))

        self.assertSequenceEqual(
            [u'Vertr\xe4ge',
             u'Aug 31, 2016',
             u'Submitted',
             u'Ziegler Robert (robert.ziegler)',
             u'Rechnungspr\xfcfungskommission',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'F\xfcr weitere Bearbeitung bewilligen'],
            [cell.value for cell in list(workbook.active.rows)[1]])

        self.assertSequenceEqual(
            [u'Antrag f\xfcr Kreiselbau',
             u'Aug 31, 2016',
             u'Active',
             u'Ziegler Robert (robert.ziegler)',
             u'Kommission f\xfcr Verkehr',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             None],
            [cell.value for cell in list(workbook.active.rows)[2]])
