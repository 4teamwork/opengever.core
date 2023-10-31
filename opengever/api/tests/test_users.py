from ftw.testbrowser import browsing
from OFS.Image import Image
from opengever.testing import IntegrationTestCase
from plone import api
from Products.CMFPlone.tests import dummy
import json


class TestUsersGet(IntegrationTestCase):

    @browsing
    def test_enumarating_user_is_possible_for_regular_user(self, browser):
        self.login(self.regular_user, browser)
        browser.open('{}/@users'.format(self.portal.absolute_url()),
                     headers=self.api_headers)

        self.assertEqual(22, len(browser.json))

    @browsing
    def test_enumarating_users_unauthorized_raises(self, browser):
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open('{}/@users'.format(self.portal.absolute_url()),
                         headers=self.api_headers)
        self.assertEqual(
            {u'message': u'Unauthorized()', u'type': u'Unauthorized'},
            browser.json)

    @browsing
    def test_accessing_an_other_user_is_possible_for_regular_user(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@users/{}'.format(
            self.portal.absolute_url(), self.dossier_responsible.id)
        browser.open(url, headers=self.api_headers)

        self.assertEquals(
            {u'username': u'robert.ziegler',
             u'description': None,
             u'roles': [u'Member'],
             u'roles_and_principals': [u'principal:robert.ziegler',
                                       u'Member',
                                       u'Authenticated',
                                       u'principal:AuthenticatedUsers',
                                       u'principal:projekt_a',
                                       u'principal:fa_users',
                                       u'Anonymous'],
             u'home_page': None,
             u'email': u'robert.ziegler@gever.local',
             u'location': None,
             u'portrait': None,
             u'fullname': u'Ziegler Robert',
             u'@id': u'http://nohost/plone/@users/robert.ziegler',
             u'id': u'robert.ziegler'}, browser.json)

    @browsing
    def test_unuathorized_accessing_an_other_user_raises(self, browser):
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            url = '{}/@users/{}'.format(
                self.portal.absolute_url(), self.dossier_responsible.id)
            browser.open(url, headers=self.api_headers)


class TestUsersPatch(IntegrationTestCase):

    @browsing
    def test_delete_user_profile_image(self, browser):
        self.login(self.regular_user, browser)
        userid = self.regular_user.id
        url = '{}/@users/{}'.format(self.portal.absolute_url(), userid)

        m_tool = api.portal.get_tool('portal_memberdata')
        m_tool._setPortrait(Image(id='avatar', file=dummy.File(), title=''), userid)

        browser.open(url, headers=self.api_headers)
        self.assertEqual(u'http://nohost/plone/portal_memberdata/portraits/kathi.barfuss', browser.json.get('portrait'))

        browser.open(url, method='PATCH', headers=self.api_headers, data=json.dumps({ 'portrait': None }))
        browser.open(url, headers=self.api_headers)
        self.assertIsNone(browser.json.get('portrait'))
