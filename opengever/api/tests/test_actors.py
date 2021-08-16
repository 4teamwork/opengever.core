from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.api.actors import serialize_actor_id_to_json_summary
import json


class TestActorSummarySerialization(IntegrationTestCase):

    @property
    def actors_url(self):
        return self.portal.absolute_url() + '/@actors'

    def test_serialize_actor_id_to_json_summary(self):
        self.assertDictEqual(
            {'@id': self.actors_url + "/some_id",
             'identifier': 'some_id'},
            serialize_actor_id_to_json_summary('some_id'))


class TestActorsGet(IntegrationTestCase):

    @property
    def actors_url(self):
        return self.portal.absolute_url() + '/@actors'

    @browsing
    def test_actors_response_for_team(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'team:1'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'active': True,
                u'actor_type': u'team',
                u'identifier': actor_id,
                u'portrait_url': None,
                u'label': u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)',
                u'representatives': [
                    {
                        u'@id': u'http://nohost/plone/@actors/kathi.barfuss',
                        u'identifier': u'kathi.barfuss',
                    },
                    {
                        u'@id': u'http://nohost/plone/@actors/robert.ziegler',
                        u'identifier': u'robert.ziegler',
                    },
                ],
                u'represents': {
                    u'@id': u'http://nohost/plone/@teams/team:1',
                },
            },
            browser.json,
        )

    @browsing
    def test_actors_response_for_inbox(self, browser):
        self.login(self.secretariat_user, browser=browser)

        actor_id = 'inbox:fa'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'active': True,
                u'actor_type': u'inbox',
                u'identifier': actor_id,
                u'portrait_url': None,
                u'label': u'Inbox: Finanz\xe4mt',
                u'representatives': [
                    {
                        u'@id': u'http://nohost/plone/@actors/jurgen.konig',
                        u'identifier': u'jurgen.konig',
                    },
                ],
                u'represents': {
                    u'@id': u'http://nohost/plone/eingangskorb/eingangskorb_fa',
                },
            },
            browser.json,
        )

    @browsing
    def test_actors_response_for_contact(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'contact:{}'.format(self.franz_meier.id)
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'active': True,
                u'actor_type': u'contact',
                u'identifier': actor_id,
                u'portrait_url': None,
                u'label': u'Meier Franz',
                u'representatives': [],
                u'represents': {
                    u'@id': u'http://nohost/plone/kontakte/meier-franz',
                },
            },
            browser.json
        )

    @browsing
    def test_actors_response_for_committee(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'committee:1'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'active': True,
                u'actor_type': u'committee',
                u'identifier': actor_id,
                u'portrait_url': None,
                u'label': u'Rechnungspr\xfcfungskommission',
                u'representatives': [
                    {
                        u'@id': u'http://nohost/plone/@actors/franzi.muller',
                        u'identifier': u'franzi.muller',
                    },
                    {
                        u'@id': u'http://nohost/plone/@actors/nicole.kohler',
                        u'identifier': u'nicole.kohler',
                    },
                ],
                u'represents': {
                    u'@id': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1',
                },
            },
            browser.json)

    @browsing
    def test_actors_response_for_ogds_user(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'jurgen.konig'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'active': True,
                u'actor_type': u'user',
                u'identifier': actor_id,
                u'portrait_url': None,
                u'label': u'K\xf6nig J\xfcrgen',
                u'representatives': [
                    {
                        u'@id': u'http://nohost/plone/@actors/jurgen.konig',
                        u'identifier': u'jurgen.konig',
                    },
                ],
                u'represents': {
                    u'@id': u'http://nohost/plone/@ogds-users/jurgen.konig',
                },
            },
            browser.json)

    @browsing
    def test_actors_response_for_group(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'projekt_a'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'active': True,
                u'actor_type': u'group',
                u'identifier': actor_id,
                u'portrait_url': None,
                u'label': u'Projekt A',
                u'representatives': [
                    {
                        'identifier': u'kathi.barfuss',
                        '@id': 'http://nohost/plone/@actors/kathi.barfuss',
                    },
                    {
                        'identifier': u'robert.ziegler',
                        '@id': 'http://nohost/plone/@actors/robert.ziegler',
                    },
                ],
                u'represents': {
                    u'@id': u'http://nohost/plone/@ogds-groups/projekt_a',
                },
            },
            browser.json)

    @browsing
    def test_actors_response_for_plone_user(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'admin'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'active': True,
                u'actor_type': u'user',
                u'identifier': actor_id,
                u'portrait_url': None,
                u'label': u'admin',
                u'representatives': [],
                u'represents': {
                    u'@id': u'http://nohost/plone/@users/admin',
                },
            },
            browser.json,
        )

    @browsing
    def test_raises_bad_request_when_actor_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.actors_url,
                         headers=self.api_headers)

        self.assertEqual(
            {"message": "Must supply an actor ID as URL path parameter.",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.actors_url + "/team:1/foo",
                         headers=self.api_headers)

        self.assertEqual(
            {"message": "Only actor ID is supported URL path parameter.",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_returns_null_actor_for_invalid_actor_id(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.actors_url + "/foo", headers=self.api_headers)

        self.assertDictEqual(
            {
                u'@id': self.actors_url + "/foo",
                u'active': False,
                u'actor_type': u'null',
                u'identifier': u'foo',
                u'portrait_url': None,
                u'label': u'foo',
                u'representatives': [],
                u'represents': None,
            },
            browser.json,
        )


class TestActorsGetListPOST(IntegrationTestCase):

    @property
    def actors_url(self):
        return self.portal.absolute_url() + '/@actors'

    @browsing
    def test_get_list_of_actors(self, browser):
        self.login(self.secretariat_user, browser=browser)

        actor_ids = {'actor_ids': ['team:1', 'inbox:fa']}
        browser.open(self.actors_url, method='POST',
                     data=json.dumps(actor_ids), headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': self.actors_url,
            u'items': [
                {
                    u'@id': self.actors_url + "/team:1",
                    u'active': True,
                    u'actor_type': u'team',
                    u'identifier': u'team:1',
                    u'portrait_url': None,
                    u'label': u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)',
                    u'representatives': [
                        {
                            u'@id': u'http://nohost/plone/@actors/kathi.barfuss',
                            u'identifier': u'kathi.barfuss',
                        },
                        {
                            u'@id': u'http://nohost/plone/@actors/robert.ziegler',
                            u'identifier': u'robert.ziegler',
                        },
                    ],
                    u'represents': {
                        u'@id': u'http://nohost/plone/@teams/team:1',
                    },
                },
                {
                    u'@id': self.actors_url + '/inbox:fa',
                    u'active': True,
                    u'actor_type': u'inbox',
                    u'identifier': u'inbox:fa',
                    u'portrait_url': None,
                    u'label': u'Inbox: Finanz\xe4mt',
                    u'representatives': [
                        {
                            u'@id': u'http://nohost/plone/@actors/jurgen.konig',
                            u'identifier': u'jurgen.konig',
                        },
                    ],
                    u'represents': {
                        u'@id': u'http://nohost/plone/eingangskorb/eingangskorb_fa',
                    },
                },
            ]
        }

        self.assertDictEqual(expected, browser.json)

    @browsing
    def test_handles_invalid_actor_ids(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_ids = {'actor_ids': ['team:1', 'foo']}
        browser.open(self.actors_url, method='POST',
                     data=json.dumps(actor_ids), headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': self.actors_url,
            u'items': [
                {
                    u'@id': self.actors_url + "/team:1",
                    u'active': True,
                    u'actor_type': u'team',
                    u'identifier': u'team:1',
                    u'portrait_url': None,
                    u'label': u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)',
                    u'representatives': [
                        {
                            u'@id': u'http://nohost/plone/@actors/kathi.barfuss',
                            u'identifier': u'kathi.barfuss',
                        },
                        {
                            u'@id': u'http://nohost/plone/@actors/robert.ziegler',
                            u'identifier': u'robert.ziegler',
                        },
                    ],
                    u'represents': {
                        u'@id': u'http://nohost/plone/@teams/team:1',
                    },
                },
                {
                    u'@id': self.actors_url + '/foo',
                    u'active': False,
                    u'actor_type': u'null',
                    u'identifier': u'foo',
                    u'portrait_url': None,
                    u'label': u'foo',
                    u'representatives': [],
                    u'represents': None,
                },
            ],
        }

        self.assertDictEqual(expected, browser.json)

    @browsing
    def test_handles_empty_actor_ids_list(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_ids = {'actor_ids': []}
        browser.open(self.actors_url, method='POST',
                     data=json.dumps(actor_ids), headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': self.actors_url,
            u'items': []
            }

        self.assertDictEqual(expected, browser.json)

    @browsing
    def test_handles_missing_actor_ids_list(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.actors_url, method='POST',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': self.actors_url,
            u'items': []
            }

        self.assertDictEqual(expected, browser.json)
