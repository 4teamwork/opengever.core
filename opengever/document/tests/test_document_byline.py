from ftw.testbrowser import browsing
from opengever.base.tests.byline_base_test import TestBylineBase
from plone.app.testing import TEST_USER_ID


class TestDocumentByline(TestBylineBase):

    @browsing
    def test_document_byline_start_date(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document)

        start_date = self.get_byline_value_by_label('Document date:')
        self.assertEquals('Jan 03, 2010', start_date.text)

    @browsing
    def test_document_byline_sequence_number(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document)

        seq_number = self.get_byline_value_by_label('Sequence number:')
        self.assertEquals('14', seq_number.text)

    @browsing
    def test_document_byline_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document)

        ref_number = self.get_byline_value_by_label('Reference number:')
        self.assertEquals('Client1 1.1 / 1 / 14', ref_number.text)

    @browsing
    def test_document_byline_document_author(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.document)

        document_author = self.get_byline_value_by_label('Author:')
        self.assertEquals(TEST_USER_ID, document_author.text)
