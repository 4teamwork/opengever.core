from ftw.testbrowser import restapi
from opengever.testing import IntegrationTestCase


class TestLivesearchGet(IntegrationTestCase):

    @restapi
    def test_livesearch(self, api_client):
        self.login(self.regular_user, api_client)
        endpoint = u'@livesearch?q={}'.format(self.document.title)
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        self.assertGreater(len(api_client.contents), 0)
        expected_result = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-11',
            u'@type': u'opengever.task.task',
            u'title': u'Vertragsentw\xfcrfe 2018',
        }
        self.assertEqual(expected_result, api_client.contents[0])

    @restapi
    def test_livesearch_limit(self, api_client):
        self.login(self.regular_user, api_client)
        endpoint = u'@livesearch?q={}&limit=1'.format(self.document.title)
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        self.assertEqual(1, len(api_client.contents))

    @restapi
    def test_livesearch_by_path(self, api_client):
        self.login(self.regular_user, api_client)
        endpoint = u'@livesearch?q={}&path={}'.format(
            self.document.title,
            self.document.absolute_url()[len(self.portal.absolute_url()):],
        )
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        self.assertEqual(1, len(api_client.contents))
        self.assertEqual(self.document.absolute_url(), api_client.contents[0]['@id'])
