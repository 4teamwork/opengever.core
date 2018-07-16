from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase
import json


class TestLivesearchGet(IntegrationTestCase):

    @browsing
    def test_livesearch(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@livesearch?q={}'.format(self.portal.absolute_url(),
                                            self.document.title)
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertGreater(len(browser.json), 0)

        entry = browser.json[0]
        self.assertIn('title', entry)
        self.assertIn('@id', entry)
        self.assertIn('@type', entry)

    @browsing
    def test_livesearch_limit(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@livesearch?q={}&limit=1'.format(self.portal.absolute_url(),
                                                    self.document.title)
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEquals(1, len(browser.json))

    @browsing
    def test_livesearch_by_path(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@livesearch?q={}&path={}'.format(
            self.portal.absolute_url(),
            self.document.title,
            '/'.join(self.document.getPhysicalPath()))

        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEquals(1, len(browser.json))
        self.assertEquals(self.document.absolute_url(), browser.json[0]['@id'])
