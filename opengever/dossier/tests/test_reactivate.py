from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone import api
from plone.protect import createToken
from Products.CMFCore.utils import getToolByName
import json


class TestReactivating(IntegrationTestCase):

    def reactivate(self, dossier, browser):
        return browser.open(dossier,
                            view='transition-reactivate',
                            data={'_authenticator': createToken()})

    def assert_errors(self, dossier, browser, error_msgs):
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(error_msgs, error_messages())

    def assert_success(self, dossier, browser, info_msgs=None):
        self.assertEquals(dossier.absolute_url(), browser.url)
        statusmessages.assert_no_error_messages()
        self.assertEquals(info_msgs, info_messages())

    def assert_reactivate_transition_invalid(self, dossier, browser):
        self.assert_errors(dossier, browser, ['Dossier is not resolved and cannot be reactivated.'])

    @browsing
    def test_reactivating_a_resolved_dossier_succesfully(self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-resolved',
                                self.resolvable_subdossier)

        self.reactivate(self.resolvable_subdossier, browser)

        self.assert_workflow_state('dossier-state-active', self.resolvable_subdossier)
        self.assert_success(self.resolvable_subdossier, browser,
                            ['Dossiers successfully reactivated.'])

    @browsing
    def test_reactivating_a_main_dossier_reactivates_subdossiers_recursively(self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-resolved',
                                self.resolvable_dossier,
                                self.resolvable_subdossier)
        subsub = create(Builder('dossier')
                        .within(self.resolvable_subdossier)
                        .in_state('dossier-state-resolved'))

        self.reactivate(self.resolvable_dossier, browser)

        self.assert_workflow_state('dossier-state-active', self.resolvable_dossier)
        self.assert_workflow_state('dossier-state-active', self.resolvable_subdossier)
        self.assert_workflow_state('dossier-state-active', subsub)

    @browsing
    def test_cannot_reactivate_an_active_dossier(self, browser):
        self.login(self.secretariat_user, browser)
        self.assert_workflow_state('dossier-state-active', self.resolvable_dossier)

        self.reactivate(self.resolvable_dossier, browser)

        self.assert_reactivate_transition_invalid(self.resolvable_dossier, browser)
        self.assert_workflow_state('dossier-state-active', self.resolvable_dossier)

    @browsing
    def test_cannot_reactivate_an_inactive_dossier(self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-inactive',
                                self.resolvable_dossier)

        self.assert_workflow_state('dossier-state-inactive', self.resolvable_dossier)
        self.reactivate(self.resolvable_dossier, browser)

        self.assert_reactivate_transition_invalid(self.resolvable_dossier, browser)
        self.assert_workflow_state('dossier-state-inactive', self.resolvable_dossier)

    @browsing
    def test_reactivating_a_subdossier_of_a_resolved_dossier_is_not_possible(self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-resolved',
                                self.resolvable_dossier,
                                self.resolvable_subdossier)

        self.reactivate(self.resolvable_subdossier, browser)

        self.assert_errors(self.resolvable_subdossier, browser,
                           ["It isn't possible to reactivate a sub dossier."])
        self.assert_workflow_state('dossier-state-resolved',
                                   self.resolvable_subdossier)

    @browsing
    def test_resets_end_dates_recursively(self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-resolved',
                                self.resolvable_dossier,
                                self.resolvable_subdossier)
        end_date = date(2013, 2, 21)
        end_date_index = self.dateindex_value_from_datetime(end_date)

        IDossier(self.resolvable_dossier).end = end_date
        IDossier(self.resolvable_subdossier).end = end_date
        self.resolvable_dossier.reindexObject(idxs=['end'])
        self.resolvable_subdossier.reindexObject(idxs=['end'])
        subsub = create(Builder('dossier')
                        .within(self.resolvable_subdossier)
                        .having(end=end_date)
                        .in_state('dossier-state-resolved'))

        self.assert_index_value(end_date_index, 'end', self.resolvable_dossier,
                                self.resolvable_subdossier, subsub)
        self.assert_metadata_value(end_date, 'end', self.resolvable_dossier,
                                   self.resolvable_subdossier, subsub)

        self.reactivate(self.resolvable_dossier, browser)

        self.assert_index_value('', 'end', self.resolvable_dossier,
                                self.resolvable_subdossier, subsub)
        self.assert_metadata_value(None, 'end', self.resolvable_dossier,
                                   self.resolvable_subdossier, subsub)
        self.assertIsNone(IDossier(self.resolvable_dossier).end)
        self.assertIsNone(IDossier(self.resolvable_subdossier).end)
        self.assertIsNone(IDossier(subsub).end)


class TestReactivatingRESTAPI(TestReactivating):

    def reactivate(self, dossier, browser, payload=None):
        browser.raise_http_errors = False
        url = dossier.absolute_url() + '/@workflow/dossier-transition-reactivate'
        kwargs = {'method': 'POST',
                  'headers': self.api_headers}
        if payload is not None:
            kwargs['data'] = json.dumps(payload)
        browser.open(url, **kwargs)

    def assert_success(self, dossier, browser, info_msgs=None):
        self.assertEqual(200, browser.status_code)
        expected_url = dossier.absolute_url() + '/@workflow/dossier-transition-reactivate'
        self.assertEquals(expected_url, browser.url)
        self.assertDictContainsSubset(
            {u'title': u'Active',
             u'comments': u'',
             u'actor': api.user.get_current().getId(),
             u'action': u'dossier-transition-reactivate',
             u'review_state': u'dossier-state-active'},
            browser.json)

    def assert_errors(self, dossier, browser, error_msgs):
        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'error': {
                u'message': u'',
                u'errors': error_msgs,
                u'type': u'PreconditionsViolated'}},
            browser.json)
        expected_url = dossier.absolute_url() + '/@workflow/dossier-transition-reactivate'
        self.assertEquals(expected_url, browser.url)

    def assert_reactivate_transition_invalid(self, dossier, browser):
        transition = 'dossier-transition-reactivate'
        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'error': {
                u'message': self.invalid_transition_message(dossier, transition),
                u'type': u'Bad Request'}},
            browser.json)
        expected_url = '{}/@workflow/{}'.format(dossier.absolute_url(), transition)
        self.assertEquals(expected_url, browser.url)

    def invalid_transition_message(self, dossier, transition):
        wftool = getToolByName(dossier, 'portal_workflow')
        actions = wftool.listActionInfos(object=dossier)
        action_ids = [action['id'] for action in actions
                      if action['category'] == 'workflow']

        message = ("Invalid transition '{}'.\n"
                   "Valid transitions are:\n"
                   "{}".format(transition, '\n'.join(sorted(action_ids))))
        return message

    @browsing
    def test_reactivating_dossier_non_recursively_is_forbidden(self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-resolved',
                                self.resolvable_dossier,
                                self.resolvable_subdossier)

        payload = {'include_children': False}
        self.reactivate(self.resolvable_dossier, browser, payload=payload)

        self.assertEqual(
            {u'error': {
                u'message': u'Reactivating dossier must always be recursive',
                u'type': u'Bad Request'}},
            browser.json)
        self.assert_workflow_state('dossier-state-resolved', self.resolvable_dossier)
