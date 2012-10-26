from opengever.base.testing import OPENGEVER_BASE_INTEGRATION_TESTING
import unittest2 as unittest
from plone.dexterity.utils import createContentInContainer
from opengever.base.source import RepositoryPathSourceBinder
from plone.app.testing import TEST_USER_ID, setRoles

class TestSourceBinder(unittest.TestCase):

    layer = OPENGEVER_BASE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Reviewer', 'Manager'])

        # Repository 1
        createContentInContainer(portal, 'opengever.repository.repositoryroot', title="Ordnungssystem1")
        reporoot1 = portal['ordnungssystem1']
        createContentInContainer(reporoot1, 'opengever.repository.repositoryfolder', title="Ordnungsposition1")
        createContentInContainer(reporoot1, 'opengever.repository.repositoryfolder', title="Ordnungsposition2")
        createContentInContainer(reporoot1, 'opengever.repository.repositoryfolder', title="Ordnungsposition3")
        repofolder2 = reporoot1['opengever.repository.repositoryfolder-1']
        createContentInContainer(repofolder2, 'opengever.repository.repositoryfolder', title="Ordnungsposition2-1")
        self.repofolder2_1 = repofolder2['opengever.repository.repositoryfolder']

        # Repository 2
        createContentInContainer(portal, 'opengever.repository.repositoryroot', title="Ordnungssystem2")
        reporoot2 = portal['ordnungssystem2']
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
