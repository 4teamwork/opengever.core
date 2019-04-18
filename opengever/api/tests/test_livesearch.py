from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestLivesearchGet(IntegrationTestCase):

    @browsing
    def test_livesearch(self, browser):
        self.login(self.regular_user, browser=browser)

        # dossier
        url = u'{}/@livesearch?q={}'.format(self.portal.absolute_url(),
                                            self.dossier.title)
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            {'@id': self.dossier.absolute_url(),
             '@type': 'opengever.dossier.businesscasedossier',
             'title': self.dossier.title,
             'filename': None},
            browser.json[0])

        # document
        url = u'{}/@livesearch?q={}'.format(self.portal.absolute_url(),
                                            self.proposaldocument.title)
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'title': self.proposaldocument.title,
             u'@id': self.proposaldocument.absolute_url(),
             u'@type': u'opengever.document.document',
             u'filename': self.proposaldocument.file.filename},
            browser.json[0])

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
            self.document.absolute_url()[len(self.portal.absolute_url()):])

        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEquals(1, len(browser.json))
        self.assertEquals(self.document.absolute_url(), browser.json[0]['@id'])
