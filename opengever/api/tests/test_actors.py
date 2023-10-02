# -*- coding: utf-8 -*-
from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from OFS.Image import Image
from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.base.interfaces import AVATAR_SOURCE_AUTO
from opengever.base.interfaces import AVATAR_SOURCE_PLONE_ONLY
from opengever.base.interfaces import AVATAR_SOURCE_PORTAL_ONLY
from opengever.base.interfaces import IActorSettings
from opengever.base.model import create_session
from opengever.contact.tests import create_contacts
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from plone import api
from Products.CMFPlone.tests import dummy
import json


class TestActorSummarySerialization(IntegrationTestCase):

    @property
    def actors_url(self):
        return self.portal.absolute_url() + '/@actors'

    def test_serialize_actor_id_to_json_summary(self):
        self.assertDictEqual(
            {'@idD': self.actors_url + "/some_id",
             'identifier': 'some_id'},
            serialize_actor_id_to_json_summary('some_id'))

    def test_serialize_unicode_actor_id_to_json_summary(self):
        self.assertDictEqual(
            {'@id': self.actors_url + u"/Utilisateurs authentifiés",
             'identifier': u'Utilisateurs authentifiés'},
            serialize_actor_id_to_json_summary(u'Utilisateurs authentifiés'))


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
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'team',
                u'identifier': actor_id,
                u'is_absent': False,
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
                    u'@id': u'http://nohost/plone/@teams/1',
                },
            },
            browser.json,
        )

    @browsing
    def test_full_representation_for_team(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'team:1'
        url = "{}/{}?full_representation=true".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertDictContainsSubset({
            u'@id': u'http://nohost/plone/@teams/1',
            u'@type': u'virtual.ogds.team',
            u'title': u'Projekt \xdcberbaung Dorfmatte'}, browser.json['represents'])

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
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'inbox',
                u'identifier': actor_id,
                u'is_absent': False,
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
    def test_full_representation_for_inbox(self, browser):
        self.login(self.secretariat_user, browser=browser)

        actor_id = 'inbox:fa'
        url = "{}/{}?full_representation=true".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertDictContainsSubset({
            u'@id': u'http://nohost/plone/eingangskorb/eingangskorb_fa',
            u'@type': u'opengever.inbox.inbox',
            u'email': u'1011033300@example.org'}, browser.json['represents'])

    @browsing
    def test_actors_response_for_contact(self, browser):
        create_contacts(self)
        self.login(self.regular_user, browser=browser)

        actor_id = 'contact:{}'.format(self.franz_meier.id)
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'contact',
                u'identifier': actor_id,
                u'is_absent': False,
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
    def test_full_representation_for_contact(self, browser):
        create_contacts(self)
        self.login(self.regular_user, browser=browser)

        actor_id = 'contact:{}'.format(self.franz_meier.id)
        url = "{}/{}?full_representation=true".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual({u'@id': u'http://nohost/plone/kontakte/meier-franz'},
                         browser.json['represents'])

    @browsing
    def test_actors_response_for_committee(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        actor_id = 'committee:1'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'committee',
                u'identifier': actor_id,
                u'is_absent': False,
                u'portrait_url': None,
                u'label': u'Rechnungspr\xfcfungskommission',
                u'representatives': [
                    {
                        u'@id': u'http://nohost/plone/@actors/nicole.kohler',
                        u'identifier': u'nicole.kohler',
                    },
                    {
                        u'@id': u'http://nohost/plone/@actors/franzi.muller',
                        u'identifier': u'franzi.muller',
                    },
                ],
                u'represents': {
                    u'@id': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1',
                },
            },
            browser.json)

    @browsing
    def test_full_representation_for_committee(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'committee:1'
        url = "{}/{}?full_representation=true".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            {u'@id': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1'},
            browser.json['represents'])

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
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'user',
                u'identifier': actor_id,
                u'is_absent': False,
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
    def test_full_representation_for_ogds_user(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'jurgen.konig'
        url = "{}/{}?full_representation=true".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictContainsSubset({
            u'@id': u'http://nohost/plone/@ogds-users/jurgen.konig',
            u'@type': u'virtual.ogds.user',
            u'email': u'jurgen.konig@gever.local'}, browser.json['represents'])

    @browsing
    def test_actors_response_for_ogds_user_with_orgunit(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'fa:jurgen.konig'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'user',
                u'identifier': actor_id,
                u'is_absent': False,
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
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'group',
                u'identifier': actor_id,
                u'is_absent': False,
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
    def test_actors_response_for_group_with_group_prefix(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'group:projekt_a'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'group',
                u'identifier': actor_id,
                u'is_absent': False,
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
    def test_full_representation_for_group(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'projekt_a'
        url = "{}/{}?full_representation=true".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictContainsSubset({
            u'@id': u'http://nohost/plone/@ogds-groups/projekt_a',
            u'@type':  u'virtual.ogds.group',
            u'title': u'Projekt A'}, browser.json['represents'])

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
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'user',
                u'identifier': actor_id,
                u'is_absent': False,
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
    def test_full_representation_for_plone_user(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = 'admin'
        url = "{}/{}?full_representation=true".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictContainsSubset({
            u'@id': u'http://nohost/plone/@users/admin',
            u'email': None,
            u'roles': [u'Manager']}, browser.json['represents'])

    @browsing
    def test_actors_response_for_system_actor(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = '__system__'
        url = "{}/{}".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'@type': u'virtual.ogds.actor',
                u'active': False,
                u'actor_type': u'system',
                u'identifier': actor_id,
                u'is_absent': False,
                u'portrait_url': None,
                u'label': u'',
                u'representatives': [],
                u'represents': None,
            },
            browser.json
        )

    @browsing
    def test_full_representation_for_system_actor(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = '__system__'
        url = "{}/{}?full_representation=true".format(self.actors_url, actor_id)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(None, browser.json['represents'])

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
                u'@type': u'virtual.ogds.actor',
                u'active': False,
                u'actor_type': u'null',
                u'identifier': u'foo',
                u'is_absent': False,
                u'portrait_url': None,
                u'label': u'Unknown ID',
                u'representatives': [],
                u'represents': None,
            },
            browser.json,
        )

    @browsing
    def test_full_representation_for_invalid_actor_id(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.actors_url + "/foo?full_representation=true", headers=self.api_headers)

        self.assertEqual(None, browser.json['represents'])

    @browsing
    def test_is_absent_if_today_is_between_absent_dates(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = self.regular_user.getId()
        url = "{}/{}".format(self.actors_url, actor_id)

        sql_user = User.query.get(self.regular_user.getId())
        sql_user.absent_from = datetime(2021, 11, 11).date()
        sql_user.absent_to = datetime(2021, 12, 15).date()
        create_session().flush()

        with freeze(datetime(2021, 12, 12)):
            browser.open(url, headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertTrue(browser.json['is_absent'])

    @browsing
    def test_is_not_absent_if_today_is_not_between_absent_dates(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = self.regular_user.getId()
        url = "{}/{}".format(self.actors_url, actor_id)

        sql_user = User.query.get(self.regular_user.getId())
        sql_user.absent_from = datetime(2021, 11, 11).date()
        sql_user.absent_to = datetime(2021, 12, 15).date()
        create_session().flush()

        with freeze(datetime(2021, 10, 12)):
            browser.open(url, headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertFalse(browser.json['is_absent'])

    @browsing
    def test_is_absent_if_absent_is_true(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = self.regular_user.getId()
        url = "{}/{}".format(self.actors_url, actor_id)

        sql_user = User.query.get(self.regular_user.getId())
        sql_user.absent = True
        create_session().flush()

        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertTrue(browser.json['is_absent'])

    @browsing
    def test_ignores_absent_dates_if_absent_is_true(self, browser):
        self.login(self.regular_user, browser=browser)

        actor_id = self.regular_user.getId()
        url = "{}/{}".format(self.actors_url, actor_id)

        sql_user = User.query.get(self.regular_user.getId())
        sql_user.absent = True
        sql_user.absent_from = datetime(2021, 11, 11).date()
        sql_user.absent_to = datetime(2021, 12, 15).date()
        create_session().flush()

        with freeze(datetime(2021, 10, 12)):
            browser.open(url, headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertTrue(browser.json['is_absent'])


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
                    u'@type': u'virtual.ogds.actor',
                    u'active': True,
                    u'actor_type': u'team',
                    u'identifier': u'team:1',
                    u'is_absent': False,
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
                        u'@id': u'http://nohost/plone/@teams/1',
                    },
                },
                {
                    u'@id': self.actors_url + '/inbox:fa',
                    u'@type': u'virtual.ogds.actor',
                    u'active': True,
                    u'actor_type': u'inbox',
                    u'identifier': u'inbox:fa',
                    u'is_absent': False,
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
                    u'@type': u'virtual.ogds.actor',
                    u'active': True,
                    u'actor_type': u'team',
                    u'identifier': u'team:1',
                    u'is_absent': False,
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
                        u'@id': u'http://nohost/plone/@teams/1',
                    },
                },
                {
                    u'@id': self.actors_url + '/foo',
                    u'@type': u'virtual.ogds.actor',
                    u'active': False,
                    u'actor_type': u'null',
                    u'identifier': u'foo',
                    u'is_absent': False,
                    u'portrait_url': None,
                    u'label': u'Unknown ID',
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

    @browsing
    def test_returns_the_plone_portrait_url_with_plone_only_setting(self, browser):
        m_tool = api.portal.get_tool('portal_memberdata')
        api.portal.set_registry_record('user_avatar_image_source',
                                       AVATAR_SOURCE_PLONE_ONLY,
                                       interface=IActorSettings)

        self.login(self.regular_user, browser=browser)
        userid = self.regular_user.id
        url = "{}/{}".format(self.actors_url, userid)
        browser.open(url, headers=self.api_headers)

        self.assertEqual(None, browser.json.get('portrait_url'))

        m_tool._setPortrait(Image(id='avatar', file=dummy.File(), title=''), userid)
        browser.open(url, headers=self.api_headers)

        self.assertEqual(
            u'http://nohost/plone/portal_memberdata/portraits/avatar',
            browser.json.get('portrait_url'))

    @browsing
    def test_returns_the_portal_portrait_url_with_portal_only_setting(self, browser):
        m_tool = api.portal.get_tool('portal_memberdata')
        api.portal.set_registry_record('user_avatar_image_source',
                                       AVATAR_SOURCE_PORTAL_ONLY,
                                       interface=IActorSettings)

        self.login(self.regular_user, browser=browser)
        userid = self.regular_user.id
        m_tool._setPortrait(Image(id='avatar', file=dummy.File(), title=''), userid)

        url = "{}/{}".format(self.actors_url, userid)
        browser.open(url, headers=self.api_headers)

        self.assertEqual(
            u'http://nohost/portal/media/avatars/2433f8fd7cd07d9cb6427016c009c2e3',
            browser.json.get('portrait_url'))

    @browsing
    def test_returns_the_portal_portrait_url_as_fallback_with_auto_setting(self, browser):
        m_tool = api.portal.get_tool('portal_memberdata')
        api.portal.set_registry_record('user_avatar_image_source',
                                       AVATAR_SOURCE_AUTO,
                                       interface=IActorSettings)

        self.login(self.regular_user, browser=browser)
        userid = self.regular_user.id
        url = "{}/{}".format(self.actors_url, userid)
        browser.open(url, headers=self.api_headers)

        self.assertEqual(
            u'http://nohost/portal/media/avatars/2433f8fd7cd07d9cb6427016c009c2e3',
            browser.json.get('portrait_url'))

        m_tool._setPortrait(Image(id='avatar', file=dummy.File(), title=''), userid)
        browser.open(url, headers=self.api_headers)

        self.assertEqual(
            u'http://nohost/plone/portal_memberdata/portraits/avatar',
            browser.json.get('portrait_url'))
