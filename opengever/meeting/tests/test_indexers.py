from collective.dexteritytextindexer.interfaces import IDynamicTextIndexExtender
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.mail import IMail
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.mail.indexer import checked_out
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from zope.component import getAdapter
from zope.component import getAdapters
from zope.interface import Interface


class TestSablonTemplateIndexers(FunctionalTestCase):

    def test_keywords_field_is_indexed_in_Subject_index(self):
        catalog = self.portal.portal_catalog

        create(Builder("sablontemplate")
               .having(keywords=(u'Keyword 1', u'Keyword with \xf6')))

        self.assertTrue(len(catalog(Subject=u'Keyword 1')),
                        'Expect one item with Keyword 1')
        self.assertTrue(len(catalog(Subject=u'Keyword with \xf6')),
                        u'Expect one item with Keyword with \xf6')

    def test_searchable_text_contains_keywords(self):
        sablon_template = create(
            Builder("sablontemplate")
            .having(keywords=(u'Pick me!', u'Keyw\xf6rd')))

        self.assertItemsEqual(
            [u'1', u'1', 'client1', 'testdokumant', 'keyword', 'me', 'pick'],
            index_data_for(sablon_template).get('SearchableText'))
