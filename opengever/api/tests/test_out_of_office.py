from datetime import datetime
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
import json


class TestOutOfOfficeGet(IntegrationTestCase):

    @browsing
    def test_get_out_of_office(self, browser):
        self.login(self.regular_user, browser=browser)

        sql_user = User.query.get(self.regular_user.getId())
        sql_user.absent = True
        sql_user.absent_from = datetime(2021, 11, 11).date()
        sql_user.absent_to = datetime(2021, 12, 11).date()
        create_session().flush()

        browser.open(self.portal, view='@out-of-office', method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual({u'@id': u'http://nohost/plone/@out-of-office',
                          u'absent': True,
                          u'absent_from': u'2021-11-11',
                          u'absent_to': u'2021-12-11'}, browser.json)


class TestOutOfOfficePatch(IntegrationTestCase):

    @browsing
    def test_patch_out_of_office(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='@out-of-office', method='PATCH',
                     data=json.dumps({'absent': True, 'absent_from': '2021-11-11',
                                      'absent_to': '2021-12-11'}),
                     headers=self.api_headers)

        self.assertEqual(204, browser.status_code)

        browser.open(self.portal, view='@out-of-office', method='GET',
                     headers=self.api_headers)

        self.assertEqual({u'@id': u'http://nohost/plone/@out-of-office',
                          u'absent': True,
                          u'absent_from': u'2021-11-11',
                          u'absent_to': u'2021-12-11'}, browser.json)

    @browsing
    def test_respects_prefer_header(self, browser):
        self.login(self.regular_user, browser)
        headers = self.api_headers.copy()
        headers.update({'Prefer': 'return=representation'})

        browser.open(self.portal, view='@out-of-office', method='PATCH',
                     data=json.dumps({'absent_from': '2021-11-11',
                                      'absent_to': '2021-12-11'}),
                     headers=headers)
        self.assertEqual(200, browser.status_code)

        self.assertEqual({u'@id': u'http://nohost/plone/@out-of-office',
                          u'absent': False,
                          u'absent_from': u'2021-11-11',
                          u'absent_to': u'2021-12-11'}, browser.json)

    @browsing
    def test_raises_if_only_one_date_is_set(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.portal, view='@out-of-office', method='PATCH',
                         data=json.dumps({'absent': True, 'absent_from': '2021-11-11'}),
                         headers=self.api_headers)

        self.assertEqual(
            {u'message': u'Either absent_from and absent_to must both be set or neither.',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_raises_if_absent_to_is_before_absent_from(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.portal, view='@out-of-office', method='PATCH',
                         data=json.dumps({'absent_from': '2021-11-16',
                                          'absent_to': '2021-07-11'}),
                         headers=self.api_headers)

        self.assertEqual(
            {u'message': u'absent_from date must be before absent_to date.',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_can_set_dates_to_none(self, browser):
        self.login(self.regular_user, browser=browser)

        sql_user = User.query.get(self.regular_user.getId())
        sql_user.absent_from = datetime(2021, 11, 11).date()
        sql_user.absent_to = datetime(2021, 12, 11).date()
        create_session().flush()

        browser.open(self.portal, view='@out-of-office', method='PATCH',
                     data=json.dumps({'absent_from': None,
                                      'absent_to': None}),
                     headers=self.api_headers)

        browser.open(self.portal, view='@out-of-office', method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual({u'@id': u'http://nohost/plone/@out-of-office',
                          u'absent': False,
                          u'absent_from': None,
                          u'absent_to': None}, browser.json)
