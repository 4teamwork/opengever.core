from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.ogds.models.user import User
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

        browser.open(self.portal, view='@substitutes/%s' % self.administrator.id, method='GET',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/@substitutes/%s' % self.administrator.id,
             u'items': [{u'@id': u'http://nohost/plone/@substitutes/%s/%s' % (self.administrator.id, self.meeting_user.id),
                         u'@type': u'virtual.ogds.substitute',
                         u'substitution_id': 1,
                         u'substitute_userid': self.meeting_user.getId(),
                         u'userid': self.administrator.getId()},
                        {u'@id': u'http://nohost/plone/@substitutes/%s/%s' % (self.administrator.id, self.dossier_responsible.id),
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


class TestSubstitutionsGet(IntegrationTestCase):
    def setUp(self):
        super(TestSubstitutionsGet, self).setUp()
        # with self.login(self.regular_user):
        self.set_substitute_and_absence(self.administrator, self.regular_user, False)
        self.set_substitute_and_absence(self.meeting_user, self.regular_user, True)
        self.set_substitute_and_absence(self.dossier_responsible, self.regular_user,
                                        False, '2018-09-01', '2018-10-01')
        self.set_substitute_and_absence(self.workspace_member, self.regular_user,
                                        True, '2018-09-01', '2018-10-01')
        self.set_substitute_and_absence(self.dossier_manager, self.regular_user,
                                        False, '2025-02-25', '2025-02-28')
        self.set_substitute_and_absence(self.secretariat_user, self.regular_user,
                                        False, '2020-10-10', '2022-02-22')
        self.set_substitute_and_absence(self.committee_responsible, self.secretariat_user, True)
        create_session().flush()

    def set_substitute_and_absence(self, user, substitute, absent, absent_from=None, absent_to=None):
        create(Builder('substitute')
               .for_user(user)
               .with_substitute(substitute))

        sql_user = User.query.get(user.getId())
        sql_user.absent = absent
        if absent_from:
            sql_user.absent_from = datetime.strptime(absent_from, '%Y-%m-%d').date()
        if absent_to:
            sql_user.absent_to = datetime.strptime(absent_to, '%Y-%m-%d').date()

    @browsing
    def test_get_substitutions(self, browser):
        self.login(self.regular_user, browser=browser)

        with freeze(datetime(2021, 11, 30)):
            browser.open(self.portal, view='@substitutions/%s' % self.regular_user.id,
                         method='GET', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(browser.json['items_total'], 6)
        self.assertEqual({self.regular_user.getId()},
                         {item['substitute_userid'] for item in browser.json['items']})

    @browsing
    def test_get_substitutions_active_substitutions(self, browser):
        self.login(self.regular_user, browser=browser)

        with freeze(datetime(2021, 11, 30)):
            browser.open(self.portal, view='@substitutions/%s?actives_only=true' % self.regular_user.id,
                         method='GET', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual({
            u'@id': u'http://nohost/plone/@substitutions/%s?actives_only=true' % self.regular_user.id,
            u'items': [
                {u'@id': u'http://nohost/plone/@substitutes/%s/%s' % (self.meeting_user.id, self.regular_user.id),
                 u'@type': u'virtual.ogds.substitute',
                 u'substitute_userid': self.regular_user.getId(),
                 u'substitution_id': 2,
                 u'userid': self.meeting_user.getId()},
                {u'@id': u'http://nohost/plone/@substitutes/%s/%s' % (self.workspace_member.id, self.regular_user.id),
                 u'@type': u'virtual.ogds.substitute',
                 u'substitute_userid': self.regular_user.getId(),
                 u'substitution_id': 4,
                 u'userid': self.workspace_member.getId()},
                {u'@id': u'http://nohost/plone/@substitutes/%s/%s' % (self.secretariat_user.id, self.regular_user.id),
                 u'@type': u'virtual.ogds.substitute',
                 u'substitute_userid': self.regular_user.getId(),
                 u'substitution_id': 6,
                 u'userid': self.secretariat_user.getId()}],
            u'items_total': 3}, browser.json)

    @browsing
    def test_get_substitutions_raises_if_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.portal, view='@substitutions', method='GET',
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
                          u'items': [{u'@id': u'http://nohost/plone/@my-substitutes/%s' % self.meeting_user.id,
                                      u'@type': u'virtual.ogds.substitute',
                                      u'substitution_id': 1,
                                      u'substitute_userid': self.meeting_user.getId(),
                                      u'userid': self.regular_user.getId()},
                                     {u'@id': u'http://nohost/plone/@my-substitutes/%s' % self.administrator.id,
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

        self.assertEqual([{u'@id': u'http://nohost/plone/@my-substitutes/%s' % self.administrator.id,
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
