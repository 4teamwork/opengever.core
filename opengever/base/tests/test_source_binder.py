from ftw.builder import Builder
from ftw.builder import create
from opengever.base.source import RepositoryPathSourceBinder
from opengever.testing import FunctionalTestCase


class TestSourceBinder(FunctionalTestCase):

    def setUp(self):
        super(TestSourceBinder, self).setUp()
        self.grant('Administrator', 'Contributor', 'Editor', 'Reader')

        # Repository 1
        reporoot1 = create(Builder('repository_root').titled('Ordnungssystem1'))
        repofolder1 = create(Builder('repository').within(reporoot1))
        repofolder2 = create(Builder('repository').within(repofolder1))
        create(Builder('repository').within(reporoot1))
        self.repofolder2_1 = create(Builder('repository').within(repofolder2))
        # Repository 2
        reporoot2 = create(Builder('repository_root').titled('Ordnungssystem2'))
        for index in range(3):
            create(Builder('repository').within(reporoot2))

    def test_sourcebinder(self):
        """
        Check if SourceBinder works correctly without a querymodificator
        """
        query = RepositoryPathSourceBinder()(self.repofolder2_1)
        self.assertEqual(
            {'query': '/plone/ordnungssystem1'},
            query.navigation_tree_query['path'])
        self.assertEqual(
            5,
            len(query.catalog.searchResults(query.navigation_tree_query)))
