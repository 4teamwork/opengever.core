from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestSubstitutesGet(IntegrationTestCase):

    @browsing
    def test_get_substitutes(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('substitute')
               .for_user(self.administrator)
               .with_substitute(self.meeting_user))

        create(Builder('substitute')
               .for_user(self.administrator)
               .with_substitute(self.dossier_responsible))

        create(Builder('substitute')
               .for_user(self.regular_user)
               .with_substitute(self.administrator))

        browser.open(self.portal, view='@substitutes/nicole.kohler', method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@substitutes/nicole.kohler',
             u'items': [{u'@id': u'http://nohost/plone/@substitutes/nicole.kohler/herbert.jager',
                         u'@type': u'virtual.ogds.substitute',
                         u'substitution_id': 1,
                         u'substitute_userid': self.meeting_user.getId(),
                         u'userid': self.administrator.getId()},
                        {u'@id': u'http://nohost/plone/@substitutes/nicole.kohler/robert.ziegler',
                         u'@type': u'virtual.ogds.substitute',
                         u'substitution_id': 2,
                         u'substitute_userid': self.dossier_responsible.getId(),
                         u'userid': self.administrator.getId()}],
             u'items_total': 2}, browser.json)

    @browsing
    def test_get_substitutes_raises_if_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.portal, view='@substitutes', method='GET',
                         headers=self.api_headers)

        self.assertEqual({u"message": u"Must supply userid as path parameter.",
                          u"type": u"BadRequest"}, browser.json)


class TestMySubstitutesGet(IntegrationTestCase):

    @browsing
    def test_get_my_substitutes(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('substitute')
               .for_user(self.regular_user)
               .with_substitute(self.meeting_user))

        create(Builder('substitute')
               .for_user(self.administrator)
               .with_substitute(self.dossier_responsible))

        create(Builder('substitute')
               .for_user(self.regular_user)
               .with_substitute(self.administrator))

        browser.open(self.portal, view='@my-substitutes', method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        self.assertEqual({u'@id': u'http://nohost/plone/@my-substitutes',
                          u'items': [{u'@id': u'http://nohost/plone/@my-substitutes/herbert.jager',
                                      u'@type': u'virtual.ogds.substitute',
                                      u'substitution_id': 1,
                                      u'substitute_userid': self.meeting_user.getId(),
                                      u'userid': self.regular_user.getId()},
                                     {u'@id': u'http://nohost/plone/@my-substitutes/nicole.kohler',
                                      u'@type': u'virtual.ogds.substitute',
                                      u'substitution_id': 3,
                                      u'substitute_userid': self.administrator.getId(),
                                      u'userid': self.regular_user.getId()}],
                          u'items_total': 2}, browser.json)


class TestMySubstitutesPost(IntegrationTestCase):

    @browsing
    def test_post_my_substitutes(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='@my-substitutes', method='POST',
                     data=json.dumps({'userid': self.administrator.getId()}),
                     headers=self.api_headers)

        self.assertEqual(204, browser.status_code)

        browser.open(self.portal, view='@my-substitutes', method='GET',
                     headers=self.api_headers)

        self.assertEqual([{u'@id': u'http://nohost/plone/@my-substitutes/nicole.kohler',
                           u'@type': u'virtual.ogds.substitute',
                           u'substitution_id': 1,
                           u'substitute_userid': self.administrator.getId(),
                           u'userid': self.regular_user.getId()}],
                         browser.json['items'])

    @browsing
    def test_post_my_substitutes_raises_if_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.portal, view='@my-substitutes', method='POST',
                         data=json.dumps({}),
                         headers=self.api_headers)

        self.assertEqual(
            {u"message": u"Property 'userid' is required", u"type": u"BadRequest"},
            browser.json)

    @browsing
    def test_post_my_substitutes_raises_if_userid_is_invalid(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.portal, view='@my-substitutes', method='POST',
                         data=json.dumps({'userid': 'invalid'}),
                         headers=self.api_headers)

        self.assertEqual(
            {u"message": u"userid 'invalid' does not exist", u"type": u"BadRequest"},
            browser.json)

    @browsing
    def test_post_my_substitutes_raises_if_substitute_already_exists(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('substitute')
               .for_user(self.regular_user)
               .with_substitute(self.administrator))

        with browser.expect_http_error(400):
            browser.open(self.portal, view='@my-substitutes', method='POST',
                         data=json.dumps({'userid': self.administrator.getId()}),
                         headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest', u'additional_metadata': {},
             u'translated_message': u'This substitute already exists.',
             u'message': u'msg_substitute_already_exists'},
            browser.json)


class TestMySubstitutesDelete(IntegrationTestCase):

    @browsing
    def test_delete_my_substitutes(self, browser):
        self.login(self.regular_user, browser=browser)
        create(Builder('substitute')
               .for_user(self.regular_user)
               .with_substitute(self.administrator))

        browser.open(self.portal, view='@my-substitutes/{}'.format(self.administrator.getId()),
                     method='DELETE', headers=self.api_headers)

        self.assertEqual(204, browser.status_code)

        browser.open(self.portal, view='@my-substitutes', method='GET',
                     headers=self.api_headers)

        self.assertEqual([], browser.json['items'])

    @browsing
    def test_delete_my_substitutes_raises_if_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.portal, view='@my-substitutes', method='DELETE',
                         headers=self.api_headers)

        self.assertEqual({u"message": u"Must supply substitute userid as path parameter.",
                          u"type": u"BadRequest"}, browser.json)

    @browsing
    def test_delete_my_substitutes_raises_if_substitute_does_not_exist(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(self.portal, view='@my-substitutes/{}'.format(self.administrator.getId()),
                         method='DELETE', headers=self.api_headers)
