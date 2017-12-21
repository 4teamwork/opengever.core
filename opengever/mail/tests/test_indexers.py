from collective.dexteritytextindexer.interfaces import IDynamicTextIndexExtender
from opengever.mail.indexer import checked_out
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from zope.component import getAdapter


class TestMailIndexers(IntegrationTestCase):

    def test_keywords_field_is_indexed_in_Subject_index(self):
        self.login(self.regular_user)
        catalog = self.portal.portal_catalog

        self.mail_eml.keywords = (u'Keyword 1', u'Keyword with \xf6')
        self.mail_eml.reindexObject()

        self.assertTrue(len(catalog(Subject=u'Keyword 1')),
                        'Expect one item with Keyword 1')
        self.assertTrue(len(catalog(Subject=u'Keyword with \xf6')),
                        u'Expect one item with Keyword with \xf6')

    def test_mail_searchable_text_contains_keywords(self):
        self.login(self.regular_user)
        self.mail_eml.keywords = (u'Pick me!', u'Keyw\xf6rd')
        self.mail_eml.reindexObject()

        index_data = index_data_for(self.mail_eml).get('SearchableText')

        self.assertIn('pick', index_data)
        self.assertIn('me', index_data)
        self.assertIn('keyword', index_data)

    def test_checked_out(self):
        self.assertEqual(checked_out(None)(), '')

    def test_reference_number(self):
        self.login(self.regular_user)
        extender = getAdapter(
            self.mail_eml, IDynamicTextIndexExtender, u'IDocumentSchema')

        self.assertEquals('Client1 1.1 / 1 / 13 13', extender())
