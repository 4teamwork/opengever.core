from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.webactions.storage import get_storage
import json


class TestWebActionsPost(IntegrationTestCase):

    HEADERS = {'Accept': 'application/json',
               'Content-Type': 'application/json'}

    @browsing
    def test_can_create_new_webaction(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions' % self.portal.absolute_url()

        action = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'enabled': True,
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
            'types': ['opengever.dossier.businesscasedossier'],
            'groups': ['some-group'],
            'permissions': ['add:opengever.document.document'],
            'comment': u'Lorem Ipsum',
            'unique_name': u'open-in-external-app-title-action',
        }
        with freeze(datetime(2019, 12, 31, 17, 45)):
            browser.open(url, method='POST', data=json.dumps(action),
                         headers=self.HEADERS)

        self.assertEqual(201, browser.status_code)
        self.assertEqual('http://nohost/plone/@webactions/0',
                         browser.headers['Location'])

        self.assertEquals({
            '@id': 'http://nohost/plone/@webactions/0',
            'action_id': 0,
            'title': 'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'enabled': True,
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
            'types': ['opengever.dossier.businesscasedossier'],
            'groups': ['some-group'],
            'permissions': ['add:opengever.document.document'],
            'comment': 'Lorem Ipsum',
            'unique_name': 'open-in-external-app-title-action',
            'created': '2019-12-31T17:45:00',
            'modified': '2019-12-31T17:45:00',
            'owner': 'webaction.manager',
        }, browser.json)

    @browsing
    def test_user_without_required_permission_cant_create_webactions(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '%s/@webactions' % self.portal.absolute_url()

        with browser.expect_unauthorized():
            browser.open(url, method='POST', data='{}', headers=self.HEADERS)

    @browsing
    def test_creating_webaction_with_incomplete_schema_fails(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions' % self.portal.absolute_url()

        action = {
            'title': u'Open in ExternalApp',
        }

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='POST', data=json.dumps(action),
                         headers=self.HEADERS)

        self.assertIn(
            "('target_url', RequiredMissing('target_url'))",
            browser.json['message'])

    @browsing
    def test_creating_webaction_validates_schema_fields(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions' % self.portal.absolute_url()

        action = {
            'title': 12345,
            'target_url': 'not-an-url',
            'display': 'nowhere-in-particular',
            'mode': 'not-in-vocabulary',
            'order': 101,
            'scope': 'invalid-scope',
        }

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='POST', data=json.dumps(action),
                         headers=self.HEADERS)

        self.assertIn(
            "('target_url', InvalidURI('not-an-url'))",
            browser.json['message'])

        self.assertIn(
            "('display', ConstraintNotSatisfied('nowhere-in-particular'))",
            browser.json['message'])

        self.assertIn(
            "('title', WrongType(12345, <type 'unicode'>, 'title'))",
            browser.json['message'])

        self.assertIn(
            "('mode', ConstraintNotSatisfied('not-in-vocabulary'))",
            browser.json['message'])

        self.assertIn(
            "('order', TooBig(101, 100))",
            browser.json['message'])

        self.assertIn(
            "('scope', ConstraintNotSatisfied('invalid-scope'))",
            browser.json['message'])

    @browsing
    def test_creating_webaction_validates_invariants(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions' % self.portal.absolute_url()

        action = {
            'title': u'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'display': 'title-buttons',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
        }

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='POST', data=json.dumps(action),
                         headers=self.HEADERS)

        self.assertEquals(
            "[(None, Invalid(\"Display location 'title-buttons' requires an icon.\",))]",
            browser.json['message'])


class TestWebActionsGet(IntegrationTestCase):

    HEADERS = {'Accept': 'application/json'}

    @browsing
    def test_lists_webactions(self, browser):
        self.login(self.webaction_manager, browser=browser)

        with freeze(datetime(2019, 12, 31, 17, 45)):
            create(Builder('webaction'))

        url = '%s/@webactions' % self.portal.absolute_url()
        browser.open(url, method='GET', headers=self.HEADERS)

        self.assertEqual(200, browser.status_code)
        self.assertEquals({
            '@id': 'http://nohost/plone/@webactions',
            'items': [{
                '@id': 'http://nohost/plone/@webactions/0',
                'action_id': 0,
                'title': 'Open in ExternalApp',
                'target_url': 'http://example.org/endpoint',
                'display': 'actions-menu',
                'mode': 'self',
                'order': 0,
                'scope': 'global',
                'created': '2019-12-31T17:45:00',
                'modified': '2019-12-31T17:45:00',
                'owner': 'webaction.manager',
            }],
        }, browser.json)

    @browsing
    def test_user_without_required_permission_cant_list_webactions(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '%s/@webactions' % self.portal.absolute_url()

        with browser.expect_unauthorized():
            browser.open(url, method='GET', headers=self.HEADERS)

    @browsing
    def test_only_lists_own_webactions(self, browser):
        self.login(self.webaction_manager, browser=browser)

        own_action = create(Builder('webaction'))
        create(Builder('webaction')
               .owned_by('someone-else'))

        url = '%s/@webactions' % self.portal.absolute_url()

        browser.open(url, method='GET', headers=self.HEADERS)
        self.assertEquals(
            [own_action['action_id']],
            [a['action_id'] for a in browser.json['items']]
        )

    @browsing
    def test_manager_can_list_all_webactions(self, browser):
        self.login(self.manager, browser=browser)

        own_action = create(Builder('webaction'))
        not_my_action = create(Builder('webaction')
                               .owned_by('someone-else'))

        url = '%s/@webactions' % self.portal.absolute_url()

        browser.open(url, method='GET', headers=self.HEADERS)
        self.assertEquals(
            [own_action['action_id'], not_my_action['action_id']],
            [a['action_id'] for a in browser.json['items']]
        )

    @browsing
    def test_get_webactions(self, browser):
        self.login(self.webaction_manager, browser=browser)

        with freeze(datetime(2019, 12, 31, 17, 45)):
            action = create(Builder('webaction'))

        url = '%s/@webactions/%s' % (self.portal.absolute_url(), action['action_id'])
        browser.open(url, method='GET', headers=self.HEADERS)

        self.assertEqual(200, browser.status_code)
        self.assertEquals({
            '@id': 'http://nohost/plone/@webactions/0',
            'action_id': 0,
            'title': 'Open in ExternalApp',
            'target_url': 'http://example.org/endpoint',
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
            'created': '2019-12-31T17:45:00',
            'modified': '2019-12-31T17:45:00',
            'owner': 'webaction.manager',
        }, browser.json)

    @browsing
    def test_get_webactions_returns_404_for_non_existent_webaction(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions/77' % self.portal.absolute_url()

        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(url, method='GET', headers=self.HEADERS)

    @browsing
    def test_user_without_required_permission_cant_get_webactions(self, browser):
        self.login(self.regular_user, browser=browser)

        action = create(Builder('webaction'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), action['action_id'])

        with browser.expect_unauthorized():
            browser.open(url, method='GET', headers=self.HEADERS)

    @browsing
    def test_user_cant_get_someone_elses_action(self, browser):
        self.login(self.webaction_manager, browser=browser)

        not_my_action = create(Builder('webaction')
                               .owned_by('someone-else'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), not_my_action['action_id'])

        with browser.expect_unauthorized():
            browser.open(url, method='GET', headers=self.HEADERS)

    @browsing
    def test_manager_may_get_any_action(self, browser):
        self.login(self.manager, browser=browser)

        not_my_action = create(Builder('webaction')
                               .owned_by('someone-else'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), not_my_action['action_id'])

        browser.open(url, method='GET', headers=self.HEADERS)
        self.assertEqual(200, browser.status_code)

    @browsing
    def test_invalid_number_of_path_params_answered_with_bad_request(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions/1/1/1/1' % self.portal.absolute_url()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='GET', headers=self.HEADERS)

    @browsing
    def test_path_param_for_action_id_must_be_integer(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions/not-an-integer' % self.portal.absolute_url()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='GET', headers=self.HEADERS)


class TestWebActionsPatch(IntegrationTestCase):

    HEADERS = {'Accept': 'application/json',
               'Content-Type': 'application/json'}

    @browsing
    def test_can_update_webaction(self, browser):
        self.login(self.webaction_manager, browser=browser)

        with freeze(datetime(2019, 12, 31, 17, 45)):
            action = create(Builder('webaction')
                            .having(
                                title=u'Open in ExternalApp',
                                target_url='http://example.org/endpoint',
            ))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), action['action_id'])

        with freeze(datetime(2020, 7, 31, 19, 15)):
            browser.open(url, method='PATCH',
                         data=json.dumps({'title': u'My new title'}),
                         headers=self.HEADERS)

        self.assertEqual(204, browser.status_code)
        self.assertEqual('', browser.contents)

        storage = get_storage()
        self.assertEqual({
            'action_id': 0,
            'title': u'My new title',
            'target_url': 'http://example.org/endpoint',
            'display': 'actions-menu',
            'mode': 'self',
            'order': 0,
            'scope': 'global',
            'created': datetime(2019, 12, 31, 17, 45),
            'modified': datetime(2020, 7, 31, 19, 15),
            'owner': 'webaction.manager',
        }, storage.get(action['action_id']))

    @browsing
    def test_update_webactions_returns_404_for_non_existent_webaction(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions/77' % self.portal.absolute_url()

        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(url, method='PATCH', headers=self.HEADERS)

    @browsing
    def test_user_without_required_permission_cant_update_webactions(self, browser):
        self.login(self.regular_user, browser=browser)

        action = create(Builder('webaction'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), action['action_id'])

        with browser.expect_unauthorized():
            browser.open(url, method='PATCH', data='{}', headers=self.HEADERS)

    @browsing
    def test_user_cant_update_someone_elses_action(self, browser):
        self.login(self.webaction_manager, browser=browser)

        not_my_action = create(Builder('webaction')
                               .owned_by('someone-else'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), not_my_action['action_id'])

        with browser.expect_unauthorized():
            browser.open(url, method='PATCH', data='{}', headers=self.HEADERS)

    @browsing
    def test_manager_may_update_any_action(self, browser):
        self.login(self.manager, browser=browser)

        not_my_action = create(Builder('webaction')
                               .owned_by('someone-else'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), not_my_action['action_id'])

        browser.open(url, method='PATCH', data='{}', headers=self.HEADERS)
        self.assertEqual(204, browser.status_code)

    @browsing
    def test_updating_webaction_validates_schema_fields(self, browser):
        self.login(self.webaction_manager, browser=browser)

        action = create(Builder('webaction'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), action['action_id'])

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='PATCH',
                         data=json.dumps({'target_url': 'not-an-url'}),
                         headers=self.HEADERS)

        self.assertIn(
            "('target_url', InvalidURI('not-an-url'))",
            browser.json['message'])

    @browsing
    def test_updating_webaction_validates_invariants(self, browser):
        self.login(self.webaction_manager, browser=browser)

        action = create(Builder('webaction')
                        .having(
                            icon_name='fa-helicopter',
                            display='title-buttons',


        ))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), action['action_id'])

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='PATCH',
                         data=json.dumps({'display': 'actions-menu'}),
                         headers=self.HEADERS)

        self.assertEqual(
            "[(None, Invalid(\"Display location 'actions-menu' doesn't allow an icon.\",))]",
            browser.json['message'])

    @browsing
    def test_invalid_number_of_path_params_answered_with_bad_request(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions/1/1/1/1' % self.portal.absolute_url()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='PATCH', headers=self.HEADERS)

    @browsing
    def test_path_param_for_action_id_must_be_integer(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions/not-an-integer' % self.portal.absolute_url()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='PATCH', headers=self.HEADERS)


class TestWebActionsDelete(IntegrationTestCase):

    HEADERS = {'Accept': 'application/json'}

    @browsing
    def test_delete_webaction(self, browser):
        self.login(self.webaction_manager, browser=browser)

        action = create(Builder('webaction'))

        url = '%s/@webactions/%s' % (self.portal.absolute_url(), action['action_id'])
        browser.open(url, method='DELETE', headers=self.HEADERS)

        self.assertEqual(204, browser.status_code)
        self.assertEqual('', browser.contents)

        storage = get_storage()
        self.assertEqual([], storage.list())

    @browsing
    def test_delete_webactions_returns_404_for_non_existent_webaction(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions/77' % self.portal.absolute_url()

        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(url, method='DELETE', headers=self.HEADERS)

    @browsing
    def test_user_without_required_permission_cant_delete_webactions(self, browser):
        self.login(self.regular_user, browser=browser)

        action = create(Builder('webaction'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), action['action_id'])

        with browser.expect_unauthorized():
            browser.open(url, method='DELETE', headers=self.HEADERS)

    @browsing
    def test_user_cant_delete_someone_elses_action(self, browser):
        self.login(self.webaction_manager, browser=browser)

        not_my_action = create(Builder('webaction')
                               .owned_by('someone-else'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), not_my_action['action_id'])

        with browser.expect_unauthorized():
            browser.open(url, method='DELETE', headers=self.HEADERS)

    @browsing
    def test_manager_may_delete_any_action(self, browser):
        self.login(self.manager, browser=browser)

        not_my_action = create(Builder('webaction')
                               .owned_by('someone-else'))
        url = '%s/@webactions/%s' % (self.portal.absolute_url(), not_my_action['action_id'])

        browser.open(url, method='DELETE', headers=self.HEADERS)
        self.assertEqual(204, browser.status_code)

    @browsing
    def test_invalid_number_of_path_params_answered_with_bad_request(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions/1/1/1/1' % self.portal.absolute_url()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='DELETE', headers=self.HEADERS)

    @browsing
    def test_path_param_for_action_id_must_be_integer(self, browser):
        self.login(self.webaction_manager, browser=browser)

        url = '%s/@webactions/not-an-integer' % self.portal.absolute_url()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(url, method='DELETE', headers=self.HEADERS)
