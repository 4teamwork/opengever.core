from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile
import json


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
            [u'Client1 1.1 / 1 / 30',
             30L,
             u'Die B\xfcrgschaft',
             u'Freddy H\xf6lderlin <from@example.org>',
             u'Jan 01, 1999',
             u'Aug 31, 2016',
             None,
             None,
             u'unchecked',
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
                 {u'width': 110, u'sortable': True, u'id': u'receipt_date'},
                 {u'width': 110, u'sortable': True, u'id': u'delivery_date'},
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

        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(browser.contents)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        self.assertEquals(
            [u'label_document_sequence_number',
             u'Title',
             u'Author',
             u'Document Date',
             u'label_document_receipt_date',
             u'label_document_delivery_date',
             u'label_document_checked_out_by',
             u'label_document_reference_number'],
            [cell.value for cell in list(workbook.active.rows)[0]])
