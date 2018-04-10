from ftw.builder import Builder
from ftw.builder import create
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase


class TestFavoriteModel(IntegrationTestCase):

    def test_add_favorite(self):
        favorite = Favorite(
            oguid=Oguid.parse('fd:123'),
            userid=self.regular_user.getId(),
            title=u'Testposition 1',
            position=2,
            portal_type='opengever.repositoryfolder.repositoryfolder',
            icon_class='contenttype-opengever-repository-repositoryfolder',
            plone_uid='127bad76e535451493bb5172c28eb38d')

        create_session().add(favorite)

        self.assertEqual(1, Favorite.query.count())
        self.assertEqual(u'Testposition 1', Favorite.query.one().title)

    def test_is_marked_as_favorite(self):
        self.login(self.regular_user)

        create(Builder('favorite')
               .for_object(self.document)
               .for_user(self.regular_user))

        create(Builder('favorite')
               .for_object(self.dossier)
               .for_user(self.dossier_responsible))

        self.assertFalse(
            Favorite.query.is_marked_as_favorite(self.document, self.dossier_responsible))
        self.assertTrue(
            Favorite.query.is_marked_as_favorite(self.document, self.regular_user))
        self.assertFalse(
            Favorite.query.is_marked_as_favorite(self.dossier, self.regular_user))
