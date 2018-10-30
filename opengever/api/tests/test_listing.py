from ftw.testbrowser import restapi
from opengever.testing import IntegrationTestCase


class TestListingEndpoint(IntegrationTestCase):

    @restapi
    def test_dossier_listing(self, api_client):
        self.login(self.regular_user, api_client)

        endpoint = (
            '@listing?name=dossiers&columns=reference&columns=title'
            '&columns=review_state&columns=responsible&sort_on=created'
        )
        api_client.open(self.repository_root, endpoint=endpoint)

        expected_last_item = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
            u'reference': u'Client1 1.1 / 1',
            u'responsible': u'robert.ziegler',
            u'review_state': u'dossier-state-active',
            u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
        }
        self.assertEqual(expected_last_item, api_client.contents['items'][-1])

    @restapi
    def test_document_listing(self, api_client):
        self.login(self.regular_user, api_client)

        endpoint = (
            '@listing?name=documents&columns=reference&columns=title'
            '&columns=modified&columns=document_author&columns=containing_dossier&sort_on=created'
        )
        api_client.open(self.dossier, endpoint=endpoint)

        expected_last_item = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
            u'containing_dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            u'document_author': u'test_user_1_',
            u'modified': u'2016-08-31T14:07:33+00:00',
            u'reference': u'Client1 1.1 / 1 / 12',
            u'title': u'Vertr\xe4gsentwurf',
        }
        self.assertEqual(expected_last_item, api_client.contents['items'][-1])

    @restapi
    def test_file_information(self, api_client):
        self.login(self.regular_user, api_client)

        endpoint = '@listing?name=documents&columns=filename&columns=filesize&sort_on=created'
        api_client.open(self.dossier, endpoint=endpoint)

        expected_last_item = {
            u'@id': self.document.absolute_url(),
            u'filesize': self.document.file.size,
            u'filename': u'Vertraegsentwurf.docx',
        }
        self.assertEqual(expected_last_item, api_client.contents['items'][-1])

    @restapi
    def test_batching(self, api_client):
        self.login(self.regular_user, api_client)

        endpoint = '@listing?name=dossiers'
        api_client.open(self.repository_root, endpoint=endpoint)
        all_dossiers = api_client.contents['items']

        # batched no start point
        endpoint = '@listing?name=dossiers&b_size=3'
        api_client.open(self.repository_root, endpoint=endpoint)
        batch_of_dossiers = api_client.contents['items']
        self.assertEqual(3, len(batch_of_dossiers))
        self.assertEqual(all_dossiers[0:3], batch_of_dossiers)

        # batched with start point
        endpoint = '@listing?name=dossiers&b_size=2&b_start=4'
        api_client.open(self.repository_root, endpoint=endpoint)
        batch_of_dossiers = api_client.contents['items']
        self.assertEqual(2, len(batch_of_dossiers))
        self.assertEqual(all_dossiers[4:6], batch_of_dossiers)

    @restapi
    def test_search_filter(self, api_client):
        self.login(self.regular_user, api_client)

        endpoint = '@listing?name=documents&search=feedback&columns=title'
        api_client.open(self.repository_root, endpoint=endpoint)
        self.assertEqual([self.taskdocument.absolute_url()], [item['@id'] for item in api_client.contents['items']])

    @restapi
    def test_current_context_is_excluded(self, api_client):
        self.login(self.regular_user, api_client)

        endpoint = '@listing?name=dossiers&columns:list=title&sort_on=created'
        api_client.open(self.dossier, endpoint=endpoint)

        self.assertNotIn(self.dossier.Title().decode('utf8'), [d['title'] for d in api_client.contents['items']])
