from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.tests.byline_base_test import TestBylineBase
from pkg_resources import resource_string


MAIL_DATA = resource_string('opengever.mail.tests', 'mail.txt')


class TestMailByline(TestBylineBase):

    def setUp(self):
        super(TestMailByline, self).setUp()
        self.grant('Manager')

        create(Builder('fixture').with_hugo_boss(email='from@example.org'))

        self.mail = create(Builder('mail')
                           .with_message(MAIL_DATA)
                           .having(start=date(2013, 11, 6),
                                   document_date=date(2013, 11, 5),
                                   document_author='hugo.boss'))
        self.browser.open(self.mail.absolute_url())

    def test_document_byline_start_date(self):
        start_date = self.get_byline_value_by_label('from:')
        self.assertEquals('Jan 01, 1999', start_date.text_content())

    def test_document_byline_sequence_number(self):
        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('1', seq_number.text_content())

    def test_document_byline_reference_number(self):
        ref_number = self.get_byline_value_by_label('Reference Number:')
        self.assertEquals('Client1 / 1', ref_number.text_content())

    def test_document_byline_document_author(self):
        document_author = self.get_byline_value_by_label('by:')
        self.assertEquals('Boss Hugo', document_author.text_content())
