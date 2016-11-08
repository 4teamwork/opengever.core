from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.mail.tests import MAIL_DATA


class TestMailByline(TestBylineBase):

    def setUp(self):
        super(TestMailByline, self).setUp()

        create(Builder('fixture').with_hugo_boss(email='from@example.org'))

        self.mail = create(Builder('mail')
                           .with_message(MAIL_DATA)
                           .having(start=date(2013, 11, 6)))

    @browsing
    def test_document_byline_start_date(self, browser):
        browser.login().open(self.mail)

        start_date = self.get_byline_value_by_label('from:')
        self.assertEquals('Jan 01, 1999', start_date.text)

    @browsing
    def test_document_byline_sequence_number(self, browser):
        browser.login().open(self.mail)

        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('1', seq_number.text)

    @browsing
    def test_document_byline_reference_number(self, browser):
        browser.login().open(self.mail)

        ref_number = self.get_byline_value_by_label('Reference Number:')
        self.assertEquals('Client1 / 1', ref_number.text)

    @browsing
    def test_document_byline_document_author(self, browser):
        browser.login().open(self.mail)

        document_author = self.get_byline_value_by_label('by:')
        self.assertEquals('Boss Hugo', document_author.text)
