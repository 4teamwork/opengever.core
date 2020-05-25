from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase


class TestSablonTemplateIndexers(FunctionalTestCase):

    def test_keywords_field_is_indexed_in_Subject_index(self):
        catalog = self.portal.portal_catalog

        create(Builder("sablontemplate")
               .having(keywords=(u'Keyword 1', u'Keyword with \xf6')))

        self.assertTrue(len(catalog(Subject=u'Keyword 1')),
                        'Expect one item with Keyword 1')
        self.assertTrue(len(catalog(Subject=u'Keyword with \xf6')),
                        u'Expect one item with Keyword with \xf6')


class TestSablonTemplateSolrIndexers(SolrIntegrationTestCase):

    def test_searchable_text_contains_keywords(self):
        self.login(self.regular_user)

        sablon_template = create(
            Builder("sablontemplate")
            .within(self.templates)
            .having(keywords=(u'Pick me!', u'Keyw\xf6rd')))

        self.commit_solr()
        indexed_value = solr_data_for(sablon_template, 'SearchableText')

        self.assertIn(u'Pick me!', indexed_value)
        self.assertIn(u'Keyw\xf6rd', indexed_value)
