from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_SOLR_INTEGRATION_TESTING
from opengever.testing import IntegrationTestCase
import random


class TestSolrIsolation(IntegrationTestCase):

    layer = OPENGEVER_SOLR_INTEGRATION_TESTING

    features = ('solr', )

    @browsing
    def test_solr_search_results_with_dynamic_content(self, browser):
        self.login(self.regular_user, browser=browser)

        random_title = u'uniqueterm%s' % str(random.randint(1, 10000))
        create(Builder('dossier')
               .titled(random_title)
               .within(self.repository_root))

        self.commit_solr()

        browser.open(self.repository_root,
                     view='@solrsearch?q=uniqueterm',
                     headers={'Accept': 'application/json'})

        result = browser.json
        self.assertEqual(1, result['items_total'])
        self.assertEqual(1, len(result['items']))
        self.assertEqual(random_title, result['items'][0]['title'])

# Create an additional copy of the above test that would fail if isolation
# didn't work between tests (i.e. if created objects in Solr would leak
# between test runs instead of getting reset to the layer snapshot).

setattr(TestSolrIsolation, 'test_solr_search_results_with_dynamic_content_1',
        TestSolrIsolation.test_solr_search_results_with_dynamic_content)
