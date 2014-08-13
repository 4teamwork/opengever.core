from opengever.base.source import RepositoryPathSourceBinder
from opengever.testing import FunctionalTestCase
from plone.dexterity.utils import createContentInContainer


class TestSourceBinder(FunctionalTestCase):

    def setUp(self):
        super(TestSourceBinder, self).setUp()
        self.grant('Reviewer', 'Manager')

        # Repository 1
        reporoot1 = createContentInContainer(self.portal, 'opengever.repository.repositoryroot', title="Ordnungssystem1")
        createContentInContainer(reporoot1, 'opengever.repository.repositoryfolder', title="Ordnungsposition1")
        repofolder2 = createContentInContainer(reporoot1, 'opengever.repository.repositoryfolder', title="Ordnungsposition2")
        createContentInContainer(reporoot1, 'opengever.repository.repositoryfolder', title="Ordnungsposition3")
        self.repofolder2_1 = createContentInContainer(repofolder2, 'opengever.repository.repositoryfolder', title="Ordnungsposition2-1")
        # Repository 2
        reporoot2 = createContentInContainer(self.portal, 'opengever.repository.repositoryroot', title="Ordnungssystem2")
        createContentInContainer(reporoot2, 'opengever.repository.repositoryfolder', title="Ordnungsposition4")
        createContentInContainer(reporoot2, 'opengever.repository.repositoryfolder', title="Ordnungsposition5")
        createContentInContainer(reporoot2, 'opengever.repository.repositoryfolder', title="Ordnungsposition6")


    def test_sourcebinder(self):
        """
        Check if SourceBinder works correctly without a querymodificator
        """
        query = RepositoryPathSourceBinder()(self.repofolder2_1)
        self.assertEqual(query.navigation_tree_query['path'], {'query': '/plone/ordnungssystem1'})
        self.assertEqual(len(query.catalog.searchResults(query.navigation_tree_query)), 5)
