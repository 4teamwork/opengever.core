from ftw.testing import MockTestCase
from opengever.dossier.browser.report import filing_no_year
from opengever.dossier.browser.report import filing_no_number

class TestMakoLaTeXView(MockTestCase):

    def test_filing_no_year(self):
        self.assertEquals(
            filing_no_year('OG-Leitung-2012-1'), 2012)
        self.assertEquals(
            filing_no_year('Leitung'), None)
        self.assertEquals(
            filing_no_year('OG-Direktion-2011-555'), 2011)
        self.assertEquals(
            filing_no_year(None), None)

    def test_filing_no_number(self):
        self.assertEquals(
            filing_no_number('OG-Leitung-2012-1'), 1)
        self.assertEquals(
            filing_no_number('Leitung'), None)
        self.assertEquals(
            filing_no_number('OG-Direktion-2011-555'), 555)
        self.assertEquals(
            filing_no_number(None), None)

