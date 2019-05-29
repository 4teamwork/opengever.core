from datetime import date
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestDossierActivation(IntegrationTestCase):

    def activate(self, dossier, browser, use_editbar=False):
        if use_editbar:
            browser.open(dossier)
            editbar.menu_option('Actions', 'dossier-transition-activate').click()
        else:
            browser.open(dossier, view='transition-activate',
                         send_authenticator=True)

    def assert_errors(self, dossier, browser, error_msgs):
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(error_msgs, error_messages())

    def assert_end_date(self, dossier, end_date):
        self.assertEqual(end_date, IDossier(dossier).end)

    def assert_success(self, dossier, browser, info_msgs=None):
        self.assertEquals(dossier.absolute_url(), browser.url)
        statusmessages.assert_no_error_messages()
        self.assertEquals(info_msgs, info_messages())

    @browsing
    def test_recursively_activates_subdossier(self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state(
            'dossier-state-inactive',
            self.dossier,
            self.subdossier,
            self.subdossier2,
            self.subsubdossier,
            )

        self.activate(self.dossier, browser, use_editbar=True)
        self.assert_success(self.dossier, browser,
                            ['The Dossier has been activated'])

        self.assert_workflow_state('dossier-state-active', self.dossier)
        self.assert_workflow_state('dossier-state-active', self.subdossier)
        self.assert_workflow_state('dossier-state-active', self.subdossier2)
        self.assert_workflow_state('dossier-state-active', self.subsubdossier)

    @browsing
    def test_activate_subdossier_is_disallowed_when_main_dossier_is_inactive(
            self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-inactive',
                                self.dossier, self.subdossier2)

        self.activate(self.subdossier2, browser)
        self.assert_errors(self.subdossier2, browser,
                           ["This subdossier can't be activated, "
                            "because the main dossiers is not active"])
        self.assert_workflow_state('dossier-state-inactive', self.subdossier2)

    @browsing
    def test_activate_subdossier_is_disallowed_when_main_dossier_is_resolved(
            self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.subdossier2)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        self.activate(self.subdossier2, browser)
        self.assert_errors(self.subdossier2, browser,
                           ["This subdossier can't be activated, "
                            "because the main dossiers is not active"])
        self.assert_workflow_state('dossier-state-inactive', self.subdossier2)

    @browsing
    def test_resets_end_dates_recursively(self, browser):
        self.login(self.secretariat_user, browser)
        IDossier(self.dossier).end = date(2013, 2, 21)
        IDossier(self.subdossier).end = date(2013, 2, 21)
        IDossier(self.subsubdossier).end = date(2013, 2, 21)

        self.set_workflow_state(
            'dossier-state-inactive',
            self.dossier,
            self.subdossier,
            self.subdossier2,
            self.subsubdossier,
            )
        self.assertIsNotNone(IDossier(self.dossier).end)
        self.assertIsNotNone(IDossier(self.subdossier).end)
        self.assertIsNotNone(IDossier(self.subsubdossier).end)

        self.activate(self.dossier, browser)

        self.assert_workflow_state('dossier-state-active', self.dossier)
        self.assert_workflow_state('dossier-state-active', self.subdossier)
        self.assert_workflow_state('dossier-state-active', self.subsubdossier)
        self.assertIsNone(IDossier(self.dossier).end)
        self.assertIsNone(IDossier(self.subdossier).end)
        self.assertIsNone(IDossier(self.subsubdossier).end)

    @browsing
    def test_end_date_is_reindexed(self, browser):
        self.login(self.secretariat_user, browser)
        enddate = date(2016, 12, 31)
        enddate_index_value = self.dateindex_value_from_datetime(enddate)

        self.assertEqual(enddate, IDossier(self.inactive_dossier).end)
        self.assert_index_value(enddate_index_value, 'end', self.inactive_dossier)
        self.assert_metadata_value(enddate, 'end', self.inactive_dossier)

        self.activate(self.inactive_dossier, browser, use_editbar=True)

        self.assert_index_value('', 'end', self.inactive_dossier)
        self.assert_metadata_value(None, 'end', self.inactive_dossier)


class TestDossierActivationRESTAPI(TestDossierActivation):

    def activate(self, dossier, browser, use_editbar=False, payload=None):
        browser.raise_http_errors = False
        url = dossier.absolute_url() + '/@workflow/dossier-transition-activate'
        kwargs = {'method': 'POST',
                  'headers': self.api_headers}
        if payload is not None:
            kwargs['data'] = json.dumps(payload)
        browser.open(url, **kwargs)

    def assert_errors(self, dossier, browser, error_msgs):
        self.assertEquals(400, browser.status_code)
        self.assertEquals(
            {u'error':
                {u'message': u'',
                 u'errors': error_msgs,
                 u'type': u'PreconditionsViolated'}},
            browser.json)
        expected_url = dossier.absolute_url() + \
            '/@workflow/dossier-transition-activate'
        self.assertEquals(expected_url, browser.url)

    def assert_success(self, dossier, browser, info_msgs=None):
        self.assertEqual(200, browser.status_code)
        expected_url = dossier.absolute_url() + '/@workflow/dossier-transition-activate'
        self.assertEquals(expected_url, browser.url)
        self.assertDictContainsSubset(
            {u'title': u'dossier-state-active',
             u'comments': u'',
             u'actor': api.user.get_current().getId(),
             u'action': u'dossier-transition-activate',
             u'review_state': u'dossier-state-active'},
            browser.json)

    @browsing
    def test_activating_dossier_non_recursively_is_forbidden(self, browser):
        self.login(self.regular_user, browser)
        payload = {'include_children': False}
        self.activate(self.inactive_dossier, browser, payload=payload)
        self.assertEqual(
            {u'error': {
                u'message': u'Activating dossier must always be recursive',
                u'type': u'Bad Request'}},
            browser.json)
        self.assert_workflow_state('dossier-state-inactive', self.inactive_dossier)
