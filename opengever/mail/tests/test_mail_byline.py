from ftw.testbrowser import browsing
from opengever.base.tests.byline_base_test import TestBylineBase


class TestMailByline(TestBylineBase):

    @browsing
    def test_document_byline_start_date(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.mail_eml)

        start_date = self.get_byline_value_by_label('from:')
        self.assertEquals('Jan 01, 1999', start_date.text)

    @browsing
    def test_document_byline_sequence_number(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.mail_eml)
        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEqual('30', seq_number.text)

    @browsing
    def test_document_byline_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.mail_eml)
        ref_number = self.get_byline_value_by_label('Reference Number:')
        self.assertEqual('Client1 1.1 / 1 / 30', ref_number.text)

    @browsing
    def test_document_byline_document_author(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.mail_eml)

        document_author = self.get_byline_value_by_label('by:')
        self.assertEquals(u'Freddy H\xf6lderlin <from@example.org>',
                          document_author.text)
