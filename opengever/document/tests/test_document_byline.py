from datetime import date
from DateTime.DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.testing import create_ogds_user
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import transaction


class TestDocumentByline(TestBylineBase):
    
    def setUp(self):
        super(TestDocumentByline, self).setUp()
        
        self.intids = getUtility(IIntIds)
        
        create_ogds_user('hugo.boss')


        self.document = create(Builder('document')
               .having(start=date(2013, 11, 6),
                       document_date=date(2013, 11, 5)))

        self.browser.open(self.document.absolute_url())
        
    def test_document_byline_icon_display(self):
        icon = self.get_byline_element_by_class('byline-icon')
        self.assertEquals('byline-icon contenttype-opengever-document-document',
                          icon.target.get('class'))
    
    def test_document_byline_start_date_display(self):
        start_date = self.get_byline_value_by_label('from:')
        self.assertEquals('Nov 05, 2013', start_date.text_content())
    
    def test_document_byline_sequence_number_display(self):
        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('1', seq_number.text_content())
        
    def test_document_byline_reference_number_display(self):
        ref_number = self.get_byline_value_by_label('Reference Number:')
        self.assertEquals('OG / 1', ref_number.text_content())
