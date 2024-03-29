from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.favorite import FavoriteManager
from opengever.base.model import CONTENT_TITLE_LENGTH
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.testing import SolrIntegrationTestCase
from opengever.trash.trash import ITrasher
from plone import api
from plone.namedfile.file import NamedBlobFile
from sqlalchemy.exc import IntegrityError
from unittest import TestCase
import json


class TestFavoriteTruncateFilename(TestCase):

    def test_truncate_filename_none(self):
        self.assertIsNone(Favorite.truncate_filename(None))

    def test_truncate_filename_empty(self):
        self.assertEqual(u'', Favorite.truncate_filename(u''))

    def test_truncate_short_filename(self):
        self.assertEqual(u'foo.txt', Favorite.truncate_filename(u'foo.txt'))

    def test_truncate_long_filename_preserves_short_extensions(self):
        expected = '{}.foo'.format(101 * 'x')
        self.assertEqual(
            expected, Favorite.truncate_filename('{}.foo'.format(200 * 'x'))
        )

    def test_truncate_long_filename_truncates_long_extensions(self):
        expected = 'foo.{}'.format(101 * 'x')
        self.assertEqual(
            expected, Favorite.truncate_filename('foo.{}'.format(200 * 'x'))
        )


class TestFavoriteModel(SolrIntegrationTestCase):

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

    def test_unique_constraint(self):
        data = {
            'oguid': Oguid.parse('fd:123'),
            'userid': self.regular_user.getId(),
            'title': u'Testposition 1',
            'position': 2,
            'portal_type': 'opengever.repositoryfolder.repositoryfolder',
            'icon_class': 'contenttype-opengever-repository-repositoryfolder',
            'plone_uid': '127bad76e535451493bb5172c28eb38d'}

        session = create_session()
        session.add(Favorite(**data))

        with self.assertRaises(IntegrityError):
            session.add(Favorite(**data))
            session.flush()

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

    def test_serialize_favorite_returns_unresolved_target_link_if_target_doesnt_exist_anymore(self):
        self.login(self.manager)
        favorite = create(Builder('favorite')
                          .for_user(self.manager)
                          .for_object(self.document))

        self.assertEqual(self.document.absolute_url(),
                         favorite.serialize(self.portal.absolute_url(), resolve=True)['target_url'])
        favorite.serialize(self.portal.absolute_url(), resolve=True)

        api.content.delete(self.document)
        self.assertEqual(u'http://nohost/plone/resolve_oguid/plone:1014073300',
                         favorite.serialize(self.portal.absolute_url(), resolve=True)['target_url'])


class TestManager(SolrIntegrationTestCase):

    @browsing
    def test_titles_of_favorites_get_truncated_on_creation(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier, view='edit')
        long_title = u''.join(u"\xe4" for i in range(400))
        browser.fill({u'Title': long_title})
        browser.click_on('Save')

        manager = FavoriteManager()
        fav = manager.add(self.regular_user.getId(), self.dossier)

        self.assertEquals(long_title[:CONTENT_TITLE_LENGTH],
                          Favorite.query.get(fav.favorite_id).title)


class TestHandlers(SolrIntegrationTestCase):

    @browsing
    def test_review_state_of_dossier_gets_updated(self, browser):
        self.login(self.regular_user)

        create(Builder('favorite')
               .for_object(self.resolvable_dossier)
               .for_user(self.regular_user))
        self.assertEquals(1, Favorite.query.count())
        favorite = Favorite.query.by_object_and_user(
            self.resolvable_dossier, self.regular_user).one()
        self.assertEqual(favorite.review_state, 'dossier-state-active')

        api.content.transition(obj=self.resolvable_dossier,
                               transition='dossier-transition-deactivate')

        favorite = Favorite.query.by_object_and_user(
            self.resolvable_dossier, self.regular_user).one()
        self.assertEqual(favorite.review_state, 'dossier-state-inactive')

    @browsing
    def test_is_subdossier_becomes_truthy_when_moved(self, browser):
        self.login(self.regular_user)

        create(Builder('favorite')
               .for_object(self.empty_dossier)
               .for_user(self.regular_user))
        self.assertEquals(1, Favorite.query.count())
        favorite = Favorite.query.by_object_and_user(
            self.empty_dossier, self.regular_user).one()
        self.assertFalse(favorite.is_subdossier)

        moved_dossier = api.content.move(self.empty_dossier, self.resolvable_dossier)

        favorite = Favorite.query.by_object_and_user(
            moved_dossier, self.regular_user).one()
        self.assertTrue(favorite.is_subdossier)

    @browsing
    def test_is_subdossier_becomes_falsy_when_moved(self, browser):
        self.login(self.regular_user)

        create(Builder('favorite')
               .for_object(self.resolvable_subdossier)
               .for_user(self.regular_user))
        self.assertEquals(1, Favorite.query.count())
        favorite = Favorite.query.by_object_and_user(
            self.resolvable_subdossier, self.regular_user).one()
        self.assertTrue(favorite.is_subdossier)

        moved_dossier = api.content.move(self.resolvable_subdossier, self.leaf_repofolder)

        favorite = Favorite.query.by_object_and_user(
            moved_dossier, self.regular_user).one()
        self.assertFalse(favorite.is_subdossier)

    @browsing
    def test_review_state_of_repository_folder_gets_updated(self, browser):
        self.login(self.administrator)

        create(Builder('favorite')
               .for_object(self.empty_repofolder)
               .for_user(self.regular_user))
        self.assertEquals(1, Favorite.query.count())
        favorite = Favorite.query.by_object_and_user(
            self.empty_repofolder, self.regular_user).one()
        self.assertEqual(favorite.review_state, 'repositoryfolder-state-active')

        api.content.transition(obj=self.empty_repofolder,
                               transition='repositoryfolder-transition-inactivate')

        favorite = Favorite.query.by_object_and_user(
            self.empty_repofolder, self.regular_user).one()
        self.assertEqual(favorite.review_state, 'repositoryfolder-state-inactive')

    @browsing
    def test_is_leafnode_becomes_falsy_when_moved(self, browser):
        # the manager can move stuff users cannot
        self.login(self.manager)

        create(Builder('favorite')
               .for_object(self.empty_repofolder)
               .for_user(self.regular_user))
        self.assertEquals(1, Favorite.query.count())
        favorite = Favorite.query.by_object_and_user(
            self.empty_repofolder, self.regular_user).one()
        self.assertTrue(favorite.is_leafnode)

        api.content.move(self.inactive_repofolder, self.empty_repofolder)

        favorite = Favorite.query.by_object_and_user(
            self.empty_repofolder, self.regular_user).one()
        self.assertFalse(favorite.is_leafnode)

    @browsing
    def test_is_leafnode_becomes_falsy_when_child_added(self, browser):
        # the manager can move stuff users cannot
        self.login(self.administrator)

        create(Builder('favorite')
               .for_object(self.empty_repofolder)
               .for_user(self.regular_user))
        self.assertEquals(1, Favorite.query.count())
        favorite = Favorite.query.by_object_and_user(
            self.empty_repofolder, self.regular_user).one()
        self.assertTrue(favorite.is_leafnode)

        create(
            Builder('repository')
            .within(self.empty_repofolder)
            .having(title_de=u'Child', title_fr=u'Child', title_en=u'Child')
        )

        favorite = Favorite.query.by_object_and_user(
            self.empty_repofolder, self.regular_user).one()
        self.assertFalse(favorite.is_leafnode)

    @browsing
    def test_is_leafnode_becomes_truthy_when_moved(self, browser):
        # the manager can move stuff users cannot
        self.login(self.manager)

        child = create(
            Builder('repository')
            .within(self.empty_repofolder)
            .having(title_de=u'Child', title_fr=u'Child', title_en=u'Child')
        )
        create(Builder('favorite')
               .for_object(self.empty_repofolder)
               .for_user(self.regular_user))
        self.assertEquals(1, Favorite.query.count())
        favorite = Favorite.query.by_object_and_user(
            self.empty_repofolder, self.regular_user).one()
        self.assertFalse(favorite.is_leafnode)

        api.content.move(child, self.branch_repofolder)

        favorite = Favorite.query.by_object_and_user(
            self.empty_repofolder, self.regular_user).one()
        self.assertTrue(favorite.is_leafnode)

    def test_all_favorites_are_deleted_when_removing_object(self):
        self.login(self.manager)

        create(Builder('favorite')
               .for_object(self.subdocument)
               .for_user(self.administrator))

        create(Builder('favorite')
               .for_object(self.subdossier)
               .for_user(self.administrator))

        create(Builder('favorite')
               .for_object(self.empty_dossier)
               .for_user(self.dossier_responsible))

        self.assertEquals(3, Favorite.query.count())

        api.content.delete(obj=self.subdossier)

        self.assertEquals(1, Favorite.query.count())

    def test_all_favorites_are_deleted_when_moving_a_document_to_trash(self):
        self.login(self.regular_user)

        create(Builder('favorite')
               .for_object(self.dossier)
               .for_user(self.administrator))

        create(Builder('favorite')
               .for_object(self.document)
               .for_user(self.dossier_responsible))

        self.assertEquals(2, Favorite.query.count())

        ITrasher(self.document).trash()

        self.assertEquals(1, Favorite.query.count())

    def test_favorite_positions_are_updated_when_deleting_object(self):
        self.login(self.manager)

        create(Builder('favorite')
               .for_object(self.document)
               .for_user(self.administrator))

        create(Builder('favorite')
               .for_object(self.subdocument)
               .for_user(self.administrator))

        create(Builder('favorite')
               .for_object(self.empty_repofolder)
               .for_user(self.administrator))

        create(Builder('favorite')
               .for_object(self.subdossier)
               .for_user(self.administrator))

        create(Builder('favorite')
               .for_object(self.empty_dossier)
               .for_user(self.administrator))

        self.assertEquals(5, Favorite.query.count())
        self.assertItemsEqual(
            [(each.position, each.favorite_id) for each in Favorite.query.all()],
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)])

        api.content.delete(obj=self.subdossier)

        self.assertEquals(3, Favorite.query.count())
        self.assertItemsEqual(
            [(each.position, each.favorite_id) for each in Favorite.query.all()],
            [(0, 1), (1, 3), (2, 5)])

    @browsing
    def test_titles_of_favorites_get_updated(self, browser):
        self.login(self.regular_user, browser=browser)

        fav1 = create(Builder('favorite')
                      .for_object(self.dossier)
                      .for_user(self.administrator)
                      .having(is_title_personalized=True,
                              title='GEVER Weeklies'))

        fav2 = create(Builder('favorite')
                      .for_object(self.dossier)
                      .for_user(self.regular_user))

        self.assertEquals('GEVER Weeklies', fav1.title)
        self.assertEquals(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung', fav2.title)

        browser.open(self.dossier, view='edit')
        browser.fill({u'Title': u'Anfragen 2018'})
        browser.click_on('Save')

        self.assertEquals('GEVER Weeklies',
                          Favorite.query.get(fav1.favorite_id).title)
        self.assertEquals(u'Anfragen 2018', Favorite.query.get(fav2.favorite_id).title)

    @browsing
    def test_titles_of_document_favorites_get_updated_on_api_patch(self, browser):
        self.login(self.regular_user, browser=browser)
        favorite = create(Builder('favorite')
                          .for_object(self.document)
                          .for_user(self.regular_user))
        self.assertEqual(u'Vertr\xe4gsentwurf', favorite.title)

        data={'title': u'\xc4nderig'}
        browser.open(
            self.document,
            data=json.dumps(data),
            method='PATCH',
            headers=self.api_headers,
        )

        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.document.title, u'\xc4nderig')
        self.assertEqual(
            u'\xc4nderig',
            Favorite.query.get(favorite.favorite_id).title
        )

    @browsing
    def test_titles_of_dossier_favorites_get_updated_on_api_patch(self, browser):
        self.login(self.regular_user, browser=browser)
        favorite = create(Builder('favorite')
                          .for_object(self.dossier)
                          .for_user(self.regular_user))
        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            favorite.title
        )

        data={'title': u'\xc4nderig'}
        browser.open(
            self.dossier,
            data=json.dumps(data),
            method='PATCH',
            headers=self.api_headers,
        )

        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.dossier.title, u'\xc4nderig')
        self.assertEqual(
            u'\xc4nderig',
            Favorite.query.get(favorite.favorite_id).title
        )

    @browsing
    def test_titles_of_document_favorites_get_updated_when_title_synced_to_filename(self, browser):
        self.login(self.regular_user, browser=browser)

        fav1 = create(Builder('favorite')
                      .for_object(self.document)
                      .for_user(self.administrator)
                      .having(is_title_personalized=True,
                              title='GEVER Weeklies'))

        fav2 = create(Builder('favorite')
                      .for_object(self.document)
                      .for_user(self.regular_user))

        self.assertEquals('GEVER Weeklies', fav1.title)
        self.assertEquals(u'Vertr\xe4gsentwurf', fav2.title)

        browser.open(self.document, view='edit')
        browser.fill({u'Title': u''})
        browser.click_on('Save')

        self.assertEquals('GEVER Weeklies',
                          Favorite.query.get(fav1.favorite_id).title)
        self.assertEquals(u'Vertraegsentwurf',
                          Favorite.query.get(fav2.favorite_id).title)

    @browsing
    def test_filenames_of_document_favorites_get_updated_when_title_is_changed(self, browser):
        self.login(self.regular_user, browser=browser)

        fav1 = create(Builder('favorite')
                      .for_object(self.document)
                      .for_user(self.administrator)
                      .having(is_title_personalized=True,
                              title='GEVER Weeklies'))

        fav2 = create(Builder('favorite')
                      .for_object(self.document)
                      .for_user(self.regular_user))

        self.assertEquals('Vertraegsentwurf.docx', fav1.filename)
        self.assertEquals('Vertraegsentwurf.docx', fav2.filename)

        browser.open(self.document, view='edit')
        browser.fill({u'Title': u'N\xe4w title'})
        browser.click_on('Save')

        self.assertEquals(u'Naew title.docx',
                          Favorite.query.get(fav1.favorite_id).filename)
        self.assertEquals(u'Naew title.docx',
                          Favorite.query.get(fav2.favorite_id).filename)

    @browsing
    def test_filenames_of_document_favorites_get_updated_when_filename_is_changed(self, browser):
        self.login(self.regular_user, browser=browser)

        fav1 = create(Builder('favorite')
                      .for_object(self.document)
                      .for_user(self.administrator)
                      .having(is_title_personalized=True,
                              title='GEVER Weeklies'))

        fav2 = create(Builder('favorite')
                      .for_object(self.document)
                      .for_user(self.regular_user))

        self.assertEquals('Vertraegsentwurf.docx', fav1.filename)
        self.assertEquals('Vertraegsentwurf.docx', fav2.filename)

        self.document.file = NamedBlobFile(
            data='New conent', filename=u'test.txt')

        # filename gets synced with title but we should have the file extension
        # of the new file
        self.assertEquals(u'Vertraegsentwurf.txt',
                          Favorite.query.get(fav1.favorite_id).filename)
        self.assertEquals(u'Vertraegsentwurf.txt',
                          Favorite.query.get(fav2.favorite_id).filename)

    @browsing
    def test_titles_of_favorites_get_truncated_on_update(self, browser):
        self.login(self.regular_user, browser=browser)

        fav = create(Builder('favorite')
                     .for_object(self.dossier)
                     .for_user(self.regular_user))

        self.assertEquals(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung', fav.title)

        browser.open(self.dossier, view='edit')
        long_title = u''.join(u"\xe4" for i in range(400))
        browser.fill({u'Title': long_title})
        browser.click_on('Save')

        self.assertEquals(long_title[:CONTENT_TITLE_LENGTH],
                          Favorite.query.get(fav.favorite_id).title)

    def test_icon_class_of_favorites_get_updated_on_checkout(self):
        self.login(self.administrator)

        fav_admin = create(Builder('favorite')
                           .for_object(self.document)
                           .for_user(self.administrator))

        fav_user = create(Builder('favorite')
                          .for_object(self.document)
                          .for_user(self.regular_user))

        # Show default document icons
        with self.login(self.administrator):
            self.assertEqual('icon-docx', fav_admin.icon_class)
        with self.login(self.regular_user):
            self.assertEqual('icon-docx', fav_user.icon_class)

        # Checkout document with regular_user
        with self.login(self.regular_user):
            self.checkout_document(self.document)

        # Show checkout-icon for document with administartor
        with self.login(self.administrator):
            self.assertEqual('icon-docx is-checked-out', fav_admin.icon_class)

        # Show self-checkout-icon for document with regular user
        with self.login(self.regular_user):
            self.assertEqual(
                'icon-docx is-checked-out-by-current-user',
                fav_user.icon_class)

    def test_icon_class_of_favorites_get_updated_on_checkin(self):
        with self.login(self.regular_user):
            self.checkout_document(self.document)

        self.login(self.administrator)

        fav_admin = create(Builder('favorite')
                           .for_object(self.document)
                           .for_user(self.administrator))

        fav_user = create(Builder('favorite')
                          .for_object(self.document)
                          .for_user(self.regular_user))

        # Checkin document again
        with self.login(self.regular_user):
            self.checkin_document(self.document)

        # Show default document icons
        with self.login(self.administrator):
            self.assertEqual('icon-docx', fav_admin.icon_class)
        with self.login(self.regular_user):
            self.assertEqual('icon-docx', fav_user.icon_class)

    def test_icon_class_of_favorites_get_updated_on_checkout_cancel(self):
        with self.login(self.regular_user):
            self.checkout_document(self.document)

        self.login(self.administrator)

        fav_admin = create(Builder('favorite')
                           .for_object(self.document)
                           .for_user(self.administrator))

        fav_user = create(Builder('favorite')
                          .for_object(self.document)
                          .for_user(self.regular_user))

        with self.login(self.regular_user):
            self.cancel_document_checkout(self.document)

        with self.login(self.administrator):
            self.assertEqual('icon-docx', fav_admin.icon_class)
        with self.login(self.regular_user):
            self.assertEqual('icon-docx', fav_user.icon_class)
