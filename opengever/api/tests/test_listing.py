from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestListingEndpoint(IntegrationTestCase):

    features = ('bumblebee',)

    @browsing
    def test_dossier_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = '&'.join((
            'name=dossiers',
            'columns=reference',
            'columns=title',
            'columns=review_state',
            'columns=responsible_fullname',
            'columns=relative_path',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.repository_root, view=view, headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'review_state': u'dossier-state-active',
             u'responsible_fullname': u'Ziegler Robert',
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
             u'reference': u'Client1 1.1 / 1',
             u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1'},
            browser.json['items'][-1])

    @browsing
    def test_document_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = '&'.join((
            'name=documents',
            'columns=reference',
            'columns=title',
            'columns=modified',
            'columns=document_author',
            'columns=containing_dossier',
            'columns=bumblebee_checksum',
            'columns=relative_path',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view, headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'reference': u'Client1 1.1 / 1 / 12',
             u'title': u'Vertr\xe4gsentwurf',
             u'document_author': u'test_user_1_',
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
             u'modified': u'2016-08-31T14:07:33+00:00',
             u'containing_dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'bumblebee_checksum': DOCX_CHECKSUM,
             u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12'},
            browser.json['items'][-1])

    @browsing
    def test_document_listing_preview_url(self, browser):
        self.login(self.regular_user, browser)
        query_string = '&'.join((
            'name=documents',
            'columns:list=preview_url',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view, headers={'Accept': 'application/json'})

        self.assertEqual(
            'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local'
            '/51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/preview',
            browser.json['items'][-1]['preview_url'][:124],
        )

    @browsing
    def test_document_listing_pdf_url(self, browser):
        self.login(self.regular_user, browser)
        query_string = '&'.join((
            'name=documents',
            'columns:list=pdf_url',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view, headers={'Accept': 'application/json'})
        self.assertEqual(
            'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local'
            '/51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/pdf',
            browser.json['items'][-1]['pdf_url'][:120],
        )

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

    @browsing
    def test_review_state_and_review_state_label(self, browser):
        self.enable_languages()

        self.login(self.regular_user, browser=browser)
        view = '@listing?name=dossiers&columns=title&columns=review_state&columns=review_state_label&sort_on=created'
        browser.open(self.dossier, view=view,
                     headers={'Accept': 'application/json',
                              'Accept-Language': 'de-ch'})

        item = browser.json['items'][0]
        self.assertEqual(u'dossier-state-active', item[u'review_state'])
        self.assertEqual(u'In Bearbeitung', item[u'review_state_label'])
