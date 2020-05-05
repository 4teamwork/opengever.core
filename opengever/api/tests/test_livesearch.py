from ftw.testbrowser import browsing
from opengever.testing import SolrIntegrationTestCase
from Products.CMFPlone.utils import safe_unicode


class TestLivesearchGet(SolrIntegrationTestCase):

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
             'filename': None,
             'is_leafnode': None,
             'is_subdossier': False,
             'review_state': 'dossier-state-active'},
            browser.json[0])

        # document
        url = u'{}/@livesearch?q={}'.format(self.portal.absolute_url(),
                                            self.proposaldocument.title)
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'title': self.proposaldocument.title,
             u'@id': self.proposaldocument.absolute_url(),
             u'@type': u'opengever.document.document',
             u'filename': self.proposaldocument.file.filename,
             u'is_leafnode': None,
             u'review_state': u'document-state-draft'},
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

    @browsing
    def test_review_state(self, browser):
        self.login(self.regular_user, browser=browser)
        url = u'{}/@livesearch?q={}&path={}'.format(
            self.portal.absolute_url(),
            self.dossier.title,
            '/'.join(self.dossier.getPhysicalPath()).replace('/plone', ''),
        )
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1, len(browser.json), 'The test has become ambiguous. Please make it more robust.')
        self.assertEqual(
            'dossier-state-active',
            browser.json[0]['review_state'],
        )

    @browsing
    def test_undeterminable_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)
        url = u'{}/@livesearch?q={}&path={}'.format(
            self.portal.absolute_url(),
            self.subtask.title,
            '/'.join(self.subtask.getPhysicalPath()).replace('/plone', ''),
        )
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1, len(browser.json), 'The test has become ambiguous. Please make it more robust.')
        self.assertNotIn('is_subdossier', browser.json[0])

    @browsing
    def test_branch_dossier_is_not_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)
        url = u'{}/@livesearch?q={}&path={}'.format(
            self.portal.absolute_url(),
            self.dossier.title,
            '/'.join(self.dossier.getPhysicalPath()).replace('/plone', ''),
        )
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1, len(browser.json), 'The test has become ambiguous. Please make it more robust.')
        self.assertFalse(browser.json[0]['is_subdossier'])

    @browsing
    def test_subdossier_is_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)
        url = u'{}/@livesearch?q={}&path={}'.format(
            self.portal.absolute_url(),
            self.subdossier2.title,
            '/'.join(self.subdossier2.getPhysicalPath()).replace('/plone', ''),
        )
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1, len(browser.json), 'The test has become ambiguous. Please make it more robust.')
        self.assertTrue(browser.json[0]['is_subdossier'])

    @browsing
    def test_undeterminable_leafnode(self, browser):
        self.login(self.regular_user, browser=browser)
        url = u'{}/@livesearch?q={}&path={}'.format(
            self.portal.absolute_url(),
            safe_unicode(self.subdocument.Title()),
            u'/'.join(self.subdocument.getPhysicalPath()).replace(u'/plone', u''),
        )
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1, len(browser.json), 'The test has become ambiguous. Please make it more robust.')
        self.assertIsNone(browser.json[0]['is_leafnode'])

    @browsing
    def test_branch_repositoryfolder_is_not_leafnode(self, browser):
        self.login(self.regular_user, browser=browser)
        url = u'{}/@livesearch?q={}&path={}'.format(
            self.portal.absolute_url(),
            safe_unicode(self.branch_repofolder.Title()),
            '/'.join(self.branch_repofolder.getPhysicalPath()).replace('/plone', ''),
        )
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1, len(browser.json), 'The test has become ambiguous. Please make it more robust.')
        self.assertFalse(browser.json[0]['is_leafnode'])

    @browsing
    def test_leaf_repositoryfolder_is_leafnode(self, browser):
        self.login(self.regular_user, browser=browser)
        url = u'{}/@livesearch?q={}&path={}'.format(
            self.portal.absolute_url(),
            safe_unicode(self.leaf_repofolder.Title()),
            u'/'.join(self.leaf_repofolder.getPhysicalPath()).replace(u'/plone', u''),
        )
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1, len(browser.json), 'The test has become ambiguous. Please make it more robust.')
        self.assertTrue(browser.json[0]['is_leafnode'])
