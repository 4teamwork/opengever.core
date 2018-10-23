from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing


class TestListingEndpoint(IntegrationTestCase):

    @browsing
    def test_dossier_listing(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=dossiers&columns=reference&columns=title&columns=review_state&columns=responsible&sort_on=created'
        browser.open(self.repository_root, view=view, headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'review_state': u'dossier-state-active',
             u'responsible': u'Ziegler Robert (robert.ziegler)',
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
             u'reference': u'Client1 1.1 / 1',
             u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'},
            browser.json['items'][-1])

    @browsing
    def test_document_listing(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&columns=reference&columns=title&columns=modified&columns=document_author&columns=containing_dossier&sort_on=created'
        browser.open(self.dossier, view=view, headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'reference': u'Client1 1.1 / 1 / 12',
             u'title': u'Vertr\xe4gsentwurf',
             u'document_author': u'test_user_1_',
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
             u'modified': u'2016-08-31T13:07:33+00:00',
             u'containing_dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'},
            browser.json['items'][-1])

    @browsing
    def test_file_information(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&columns=filename&columns=filesize&sort_on=created'
        browser.open(self.dossier, view=view, headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'@id': self.document.absolute_url(),
             u'filesize': self.document.file.size,
             u'filename': u'Vertraegsentwurf.docx'},
            browser.json['items'][-1])

    @browsing
    def test_batching(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=dossiers'
        browser.open(
            self.repository_root, view=view, headers={'Accept': 'application/json'})
        all_dossiers = browser.json['items']

        # batched no start point
        view = '@listing?name=dossiers&b_size=3'
        browser.open(
            self.repository_root, view=view, headers={'Accept': 'application/json'})
        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(all_dossiers[0:3], browser.json['items'])

        # batched with start point
        view = '@listing?name=dossiers&b_size=2&b_start=4'
        browser.open(
            self.repository_root, view=view, headers={'Accept': 'application/json'})
        self.assertEqual(2, len(browser.json['items']))
        self.assertEqual(all_dossiers[4:6], browser.json['items'])

    @browsing
    def test_search_filter(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&search=feedback&columns=title'
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})
        self.assertEqual(
            [self.taskdocument.absolute_url()],
            [item['@id'] for item in browser.json['items']])

    @browsing
    def test_current_context_is_excluded(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=dossiers&columns:list=title&sort_on=created'
        browser.open(
            self.dossier, view=view, headers={'Accept': 'application/json'})

        self.assertNotIn(
            self.dossier.Title().decode('utf8'),
            [d['title'] for d in browser.json['items']],
        )
