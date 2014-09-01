from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.testing import create_ogds_user


class TestDocumentByline(TestBylineBase):

    def setUp(self):
        super(TestDocumentByline, self).setUp()
        self.grant('Manager')
        create_ogds_user('hugo.boss')

        self.document = create(Builder('document')
                               .having(start=date(2013, 11, 6),
                                       document_date=date(2013, 11, 5),
                                       document_author='hugo.boss'))

        self.browser.open(self.document.absolute_url())

    def test_document_byline_start_date(self):
        start_date = self.get_byline_value_by_label('from:')
        self.assertEquals('Nov 05, 2013', start_date.text_content())

    def test_document_byline_sequence_number(self):
        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('1', seq_number.text_content())

    def test_document_byline_reference_number(self):
        ref_number = self.get_byline_value_by_label('Reference Number:')
        self.assertEquals('Client1 / 1', ref_number.text_content())

    def test_document_byline_document_author(self):
        document_author = self.get_byline_value_by_label('by:')
        self.assertEquals('Boss Hugo', document_author.text_content())
