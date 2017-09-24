from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.usermigration.repo_favorites import RepoFavoritesMigrator
from opengever.portlets.tree.interfaces import IRepositoryFavorites
from zope.component import getMultiAdapter


class TestRepoFavoritesMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestRepoFavoritesMigrator, self).setUp()
        self.portal = self.layer['portal']

        self.root = create(Builder('repository_root'))

        self.old_ogds_user = create(Builder('ogds_user')
                                    .id('HANS.MUSTER')
                                    .having(active=False))
        self.new_ogds_user = create(Builder('ogds_user')
                                    .id('hans.muster')
                                    .having(active=True))

    def favorites_for(self, username):
        return getMultiAdapter((self.root, username), IRepositoryFavorites)

    def test_migrates_repo_favorites(self):
        self.favorites_for('HANS.MUSTER').add('foo')

        RepoFavoritesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals(['foo'], self.favorites_for('hans.muster').list())
        self.assertEquals([], self.favorites_for('HANS.MUSTER').list())

    def test_merges_old_and_new_repo_favorites(self):
        self.favorites_for('HANS.MUSTER').set(['foo', 'bar'])
        self.favorites_for('hans.muster').set(['bar', 'qux'])

        RepoFavoritesMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals(['bar', 'qux', 'foo'],
                          self.favorites_for('hans.muster').list())
        self.assertEquals([], self.favorites_for('HANS.MUSTER').list())
