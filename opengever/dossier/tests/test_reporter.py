from datetime import datetime
from ftw.testbrowser import browsing
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.filing.report import filing_no_filing
from opengever.dossier.filing.report import filing_no_number
from opengever.dossier.filing.report import filing_no_year
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile
import json


class TestDossierReporter(IntegrationTestCase):

    @browsing
    def test_dossier_report(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(view='dossier_report',
                     data=self.make_path_param(self.dossier, self.inactive_dossier))

        data = browser.contents
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        rows = list(workbook.active.rows)

        self.assertSequenceEqual(
            [self.dossier.title,
             datetime(2016, 1, 1),
             None,
             u'Ziegler Robert (robert.ziegler)',
             u'dossier-state-active',
             u'Client1 1.1 / 1'],
            [cell.value for cell in rows[1]])

        self.assertSequenceEqual(
            [self.inactive_dossier.title,
             datetime(2016, 1, 1, 0, 0),
             datetime(2016, 12, 31, 0, 0),
             u'Ziegler Robert (robert.ziegler)',
             u'dossier-state-inactive',
             u'Client1 1.1 / 3'],
            [cell.value for cell in rows[2]])

    @browsing
    def test_respects_column_tabbedview_settings_if_exists(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {'view_name': 'mydossiers',
                'gridstate': json.dumps({
                    "columns":[
                        {"id":"path_checkbox","width":30},
                        {"id":"sortable_title","width":300,"sortable":True},
                        {"id":"review_state","width":110,"sortable":True},
                        {"id":"reference","width":110,"sortable":True},
                        {"id":"end","width":110,"sortable":True},
                        {"id":"responsible","width":110,"sortable":True},
                        {"id":"start","width":110,"hidden":True,"sortable":True},
                        {"id":"Subject","width":110,"sortable":True},
                        {"id":"dummy","width":1,"hidden":True}],
                    "sort":{"field":"modified","direction":"ASC"}})}
        browser.open(view='@@tabbed_view/setgridstate', data=data)


        data = self.make_path_param(self.dossier, self.inactive_dossier)
        data['view_name'] = 'mydossiers'
        browser.open(view='dossier_report', data=data)

        data = browser.contents
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        rows = list(workbook.active.rows)
        self.assertSequenceEqual(
            [u'Title', u'Review state', u'Reference Number', u'Closing Date',
             u'Responsible'],
            [cell.value for cell in rows[0]])

    @browsing
    def test_report_appends_filing_fields(self, browser):
        self.activate_feature('filing_number')
        self.login(self.regular_user, browser=browser)

        IFilingNumber(self.dossier).filing_no = u'Client1-Leitung-2012-1'
        self.dossier.reindexObject()

        browser.open(view='dossier_report',
                     data=self.make_path_param(self.dossier))

        data = browser.contents
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        labels = [cell.value for cell in list(workbook.active.rows)[0]]
        self.assertIn(u'filing_no_filing', labels)
        self.assertIn(u'filing_no_year', labels)
        self.assertIn(u'filing_no_number', labels)
        self.assertIn(u'Filing number', labels)

        self.assertSequenceEqual(
            [self.dossier.title,
             datetime(2016, 1, 1),
             None,
             u'Ziegler Robert (robert.ziegler)',
             u'Leitung',
             2012,
             1,
             u'Client1-Leitung-2012-1',
             u'dossier-state-active',
             u'Client1 1.1 / 1'],
            [cell.value for cell in list(workbook.active.rows)[1]])

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
