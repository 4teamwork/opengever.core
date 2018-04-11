from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase


class TestFavoriteAction(IntegrationTestCase):

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
    def test_favorite_action_is_disabled_on_wrapper_objects(self, browser):
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
            '', browser.css('#mark-as-favorite').first.get('class'))
