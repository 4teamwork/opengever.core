from ftw.testbrowser import restapi
from opengever.api.testing import RelativeSession
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD


class TestGeverJSONSummarySerializer(IntegrationTestCase):

    def setUp(self):
        super(TestGeverJSONSummarySerializer, self).setUp()

        self.api = RelativeSession(self.portal.absolute_url())
        self.api.headers.update({'Accept': 'application/json'})
        self.api.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']

    @restapi
    def test_portal_type_is_included(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.repository_root)
        repofolder_summary = api_client.contents['items'][0]
        self.assertDictContainsSubset({u'@type': u'opengever.repository.repositoryfolder'}, repofolder_summary)

        api_client.open(self.leaf_repofolder)
        dossier_summary = api_client.contents['items'][0]
        self.assertDictContainsSubset({u'@type': u'opengever.dossier.businesscasedossier'}, dossier_summary)

    @restapi
    def test_translated_title_contained_in_summary_if_obj_translated(self, api_client):
        self.login(self.regular_user, api_client)

        api_client.open(self.repository_root, headers={'Accept': 'application/json', 'Accept-Language': 'de-ch'})
        self.assertDictContainsSubset({u'title': u'1. F\xfchrung'}, api_client.contents['items'][0])

        api_client.open(self.repository_root, headers={'Accept': 'application/json', 'Accept-Language': 'fr-ch'})
        self.assertDictContainsSubset({u'title': u'1. Direction'}, api_client.contents['items'][0])

    @restapi
    def test_translated_titles_default_to_german(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.repository_root)
        self.assertDictContainsSubset({u'title': u'1. F\xfchrung'}, api_client.contents['items'][0])

    @restapi
    def test_regular_title_in_summary_if_obj_not_translated(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.leaf_repofolder)
        self.assertDictContainsSubset(
            {u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'},
            api_client.contents['items'][0],
        )

    @restapi
    def test_summary_with_custom_field_list(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.dossier, endpoint='?items.fl=filesize,filename,modified,created,mimetype,creator,changed')
        expected_summary = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
            u'changed': u'2016-08-31T14:07:33+00:00',
            u'created': u'2016-08-31T14:07:33+00:00',
            u'creator': u'robert.ziegler',
            u'filename': u'Vertraegsentwurf.docx',
            u'filesize': 27413,
            u'mimetype': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'modified': u'2016-08-31T14:07:33+00:00',
        }
        self.assertEqual(expected_summary, api_client.contents['items'][0])

    @restapi
    def test_summary_with_reference_number(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.dossier, endpoint='?items.fl=reference_number')

        expected_summary = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
            u'reference_number': u'Client1 1.1 / 1 / 12',
        }
        self.assertEqual(expected_summary, api_client.contents['items'][0])

    @restapi
    def test_summary_with_filename_on_dossiers_containing_tasks(self, api_client):
        self.login(self.regular_user, api_client)
        self.task.text = u'Sample description'
        api_client.open(self.dossier, endpoint='?items.fl=filename,filesize')
        expected_summary = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1',
            u'filename': None,
            u'filesize': 0,
        }
        self.assertEqual(expected_summary, api_client.contents['items'][10])
