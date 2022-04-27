from ftw.testbrowser import browsing
from io import BytesIO
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
import json


class TestDocumentReporter(IntegrationTestCase):

    def load_workbook(self, data):
        return load_workbook(BytesIO(data))

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
            # /plone/ordnungssystem/...
            data=self.make_path_param(self.document, self.mail_eml))

        workbook = self.load_workbook(browser.contents)

        # One title row and two data rows
        self.assertEquals(3, len(list(workbook.active.rows)))

        self.assertSequenceEqual(
            [u'Client1 1.1 / 1 / 14',
             14,
             u'Vertr\xe4gsentwurf',
             u'test-user (test_user_1_)',
             u'Jan 03, 2010',
             u'Jan 03, 2010',
             u'Jan 03, 2010',
             None,
             u'not assessed',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            [cell.value for cell in list(workbook.active.rows)[1]])

        self.assertSequenceEqual(
            [u'Client1 1.1 / 1 / 29',
             29,
             u'Die B\xfcrgschaft',
             u'Freddy H\xf6lderlin <from@example.org>',
             u'Jan 01, 1999',
             u'Aug 31, 2016',
             None,
             None,
             u'not assessed',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            [cell.value for cell in list(workbook.active.rows)[2]])

    @browsing
    def test_document_report_with_pseudorelative_path(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(
            view='document_report',
            # /ordnungssystem/...
            data=self.make_pseudorelative_path_param(self.document, self.mail_eml))

        workbook = self.load_workbook(browser.contents)

        # One title row and two data rows
        self.assertEquals(3, len(list(workbook.active.rows)))

        self.assertSequenceEqual(
            [u'Client1 1.1 / 1 / 14',
             14,
             u'Vertr\xe4gsentwurf',
             u'test-user (test_user_1_)',
             u'Jan 03, 2010',
             u'Jan 03, 2010',
             u'Jan 03, 2010',
             None,
             u'not assessed',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            [cell.value for cell in list(workbook.active.rows)[1]])

        self.assertSequenceEqual(
            [u'Client1 1.1 / 1 / 29',
             29,
             u'Die B\xfcrgschaft',
             u'Freddy H\xf6lderlin <from@example.org>',
             u'Jan 01, 1999',
             u'Aug 31, 2016',
             None,
             None,
             u'not assessed',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            [cell.value for cell in list(workbook.active.rows)[2]])

    @browsing
    def test_respects_column_tabbedview_settings_if_exists(self, browser):
        self.login(self.regular_user, browser=browser)

        grid_state = json.dumps(
            {u'sort': {u'field': u'sequence_number', u'direction': u'ASC'},
             u'columns': [
                 {u'width': 30, u'id': u'path_checkbox'},
                 {u'width': 110, u'sortable': True, u'id': u'sequence_number'},
                 {u'width': 200, u'sortable': True, u'id': u'sortable_title'},
                 {u'width': 110, u'sortable': True, u'id': u'sortable_author'},
                 {u'width': 110, u'sortable': True, u'id': u'document_date'},
                 {u'width': 110, u'hidden': True, u'sortable': True, u'id': u'changed'},
                 {u'width': 110, u'hidden': True, u'sortable': True, u'id': u'created'},
                 {u'width': 110, u'sortable': True, u'id': u'receipt_date'}, {u'width': 110, u'sortable': True, u'id': u'delivery_date'},
                 {u'width': 110, u'sortable': True, u'id': u'checked_out'},
                 {u'width': 110, u'sortable': True, u'hidden': True, u'id': u'public_trial'},
                 {u'width': 110, u'sortable': True, u'id': u'reference'},
                 {u'width': 110, u'sortable': True, u'id': u'file_extension'},
                 {u'width': 110, u'id': u'Subject'},
                 {u'width': 1, u'hidden': True, u'id': u'dummy'}]})

        data = {'view_name': 'mydocuments',
                'gridstate': grid_state}
        browser.open(view='@@tabbed_view/setgridstate', data=data)

        data = self.make_path_param(self.document, self.mail_eml)
        data['view_name'] = 'mydocuments'
        browser.open(view='document_report', data=data)

        workbook = self.load_workbook(browser.contents)

        self.assertEquals(
            [u'Sequence number',
             u'Title',
             u'Author',
             u'Document date',
             u'label_document_receipt_date',
             u'label_document_delivery_date',
             u'Checked out by',
             u'Reference number'],
            [cell.value for cell in list(workbook.active.rows)[0]])
