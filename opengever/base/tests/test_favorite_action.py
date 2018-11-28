from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.base.viewlets.favorite_action import FavoriteETagValue
from opengever.document.browser.tabbed import DocumentTabbedView
from opengever.testing import IntegrationTestCase


class TestFavoriteAction(IntegrationTestCase):

    features = ('favorites', )

    @browsing
    def test_favorite_link_is_shown_on_dexterity_object(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        viewlet = browser.css('#favorite-action').first
        self.assertIsNotNone(viewlet)
        self.assertEquals(Oguid.for_object(self.dossier).id,
                          viewlet.get('data-oguid'))
        self.assertEquals('http://nohost/plone/@favorites/kathi.barfuss',
                          viewlet.get('data-url'))

    @browsing
    def test_favorite_action_respects_feature_flag(self, browser):
        self.deactivate_feature('favorites')

        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        self.assertEqual([], browser.css('#favorite-action'))

    @browsing
    def test_favorite_action_is_disabled_on_wrapper_objects(self, browser):
        self.activate_feature('meeting')
        self.login(self.meeting_user, browser=browser)
        browser.open(self.meeting)

        self.assertEqual([], browser.css('#favorite-action'))

    @browsing
    def test_adds_is_favorite_class_when_favorite_exists(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.dossier))

        browser.open(self.dossier)
        self.assertEqual(
            'is-favorite', browser.css('#mark-as-favorite').first.get('class'))

        browser.open(self.document)
        self.assertEqual(
            None, browser.css('#mark-as-favorite').first.get('class'))


class TestFavoriteEtagValue(IntegrationTestCase):
    """Exceptions in the etag value adapter are failing silently,
    therefore we tests the etag adapter unittest like.
    """

    features = ('favorites', )

    def test_handles_regular_requests(self):
        self.login(self.regular_user)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.document))

        view = DocumentTabbedView(self.document, None)
        value = FavoriteETagValue(view, None)()
        self.assertEqual('1', value)

    def test_handles_webdav_requests(self):
        self.login(self.regular_user)

        create(Builder('favorite')
               .for_user(self.regular_user)
               .for_object(self.document))

        value = FavoriteETagValue(self.document, None)()
        self.assertEqual('1', value)
