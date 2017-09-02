from datetime import datetime
from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import activate_filing_number
from opengever.core.testing import inactivate_filing_number
from opengever.dossier.filing.report import filing_no_filing
from opengever.dossier.filing.report import filing_no_number
from opengever.dossier.filing.report import filing_no_year
from opengever.testing import FunctionalTestCase
from openpyxl import load_workbook
from plone.app.testing import TEST_USER_ID
from tempfile import NamedTemporaryFile


class TestDossierReporterWithFilingNumberSupport(FunctionalTestCase):

    def setUp(self):
        super(TestDossierReporterWithFilingNumberSupport, self).setUp()
        activate_filing_number(self.portal)

        self.dossier = create(Builder('dossier')
                              .titled(u'Export1 Dossier')
                              .having(start=date(2012, 1, 1),
                                      end=date(2012, 12, 1),
                                      responsible=TEST_USER_ID,
                                      filing_no='Client1-Leitung-2012-1')
                              .in_state('active'))

    def tearDown(self):
        super(TestDossierReporterWithFilingNumberSupport, self).tearDown()
        inactivate_filing_number(self.portal)

    @browsing
    def test_report_appends_filing_fields(self, browser):
        browser.login().open(view='dossier_report',
                             data={'paths:list': [
                                   '/'.join(self.dossier.getPhysicalPath()),
                                   ]})

        data = browser.contents
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        self.assertSequenceEqual(
            [u'Export1 Dossier',
             datetime(2012, 1, 1),
             datetime(2012, 12, 1),
             u'Test User (test_user_1_)',
             u'Leitung',
             2012.0,
             1.0,
             u'Client1-Leitung-2012-1',
             u'active',
             u'Client1 / 1'],
            [cell.value for cell in list(workbook.active.rows)[1]])


class TestDossierReporter(FunctionalTestCase):

    def setUp(self):
        super(TestDossierReporter, self).setUp()

        self.dossier1 = create(Builder('dossier')
                               .titled(u'Export1 Dossier')
                               .having(start=date(2012, 1, 1),
                                       end=date(2012, 12, 1),
                                       responsible=TEST_USER_ID)
                               .in_state('active'))

        self.dossier2 = create(Builder('dossier')
                               .titled(u'Foo Dossier')
                               .having(start=date(2012, 1, 1),
                                       end=date(2012, 12, 1),
                                       responsible=TEST_USER_ID)
                               .in_state('active'))

    @browsing
    def test_dossier_report(self, browser):
        pass
        browser.login().open(view='dossier_report',
                             data={'paths:list': [
                                   '/'.join(self.dossier1.getPhysicalPath()),
                                   '/'.join(self.dossier2.getPhysicalPath())
                                   ]})

        data = browser.contents
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        rows = list(workbook.active.rows)

        self.assertSequenceEqual(
            [u'Export1 Dossier',
             datetime(2012, 1, 1),
             datetime(2012, 12, 1),
             u'Test User (test_user_1_)',
             u'active',
             u'Client1 / 1'],
            [cell.value for cell in rows[1]])
        self.assertSequenceEqual(
            [u'Foo Dossier',
             datetime(2012, 1, 1),
             datetime(2012, 12, 1),
             u'Test User (test_user_1_)',
             u'active',
             u'Client1 / 2'],
            [cell.value for cell in rows[2]])

    def test_filing_no_year(self):
        self.assertEquals(
            filing_no_year('Client1-Leitung-2012-1'), 2012)
        self.assertEquals(
            filing_no_year('Leitung'), None)
        self.assertEquals(
            filing_no_year('Client1-Direktion-2011-555'), 2011)
        self.assertEquals(
            filing_no_year(None), None)

    def test_filing_no_number(self):
        self.assertEquals(
            filing_no_number('Client1-Leitung-2012-1'), 1)
        self.assertEquals(
            filing_no_number('Leitung'), None)
        self.assertEquals(
            filing_no_number('Client1-Direktion-2011-555'), 555)
        self.assertEquals(
            filing_no_number(None), None)

    def test_filing_no_filing(self):
        self.assertEquals(
            filing_no_filing('Client1-Leitung-2012-1'), 'Leitung')
        self.assertEquals(
            filing_no_filing('Leitung'), 'Leitung')
        self.assertEquals(
            filing_no_filing('Client1-Direktion-2011-555'), 'Direktion')
        self.assertEquals(
            filing_no_filing(None), None)
