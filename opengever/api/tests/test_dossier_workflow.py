from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.dossier.resolve import LockingResolveManager
from opengever.testing import IntegrationTestCase
from plone import api


class TestDossierWorkflowRESTAPITransitions(IntegrationTestCase):
    """This test suite exercises the possible dossier workflow transitions
    via the REST API.

    It does so on a very high level, for the happy path, and doesn't assert
    on all the aspects of the resulting state, post-transition jobs etc.

    More detailed tests for the specific transitions can be found in
    opengever.dossier.tests.
    """

    def assert_state(self, expected_state, obj):
        self.assertEquals(expected_state,
                          api.content.get_state(obj))

    def api_transition(self, obj, transition, browser):
        url = '/'.join((obj.absolute_url(), '@workflow', transition))
        browser.open(
            url,
            headers={'Accept': 'application/json'},
            method='POST')

    @browsing
    def test_resolve_via_restapi(self, browser):
        self.login(self.secretariat_user, browser)
        self.assert_state('dossier-state-active', self.resolvable_dossier)

        with freeze(datetime(2018, 4, 30)):
            self.api_transition(
                self.resolvable_dossier, 'dossier-transition-resolve', browser)

        self.assert_state('dossier-state-resolved', self.resolvable_dossier)
        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {u'title': u'dossier-state-resolved',
             u'comments': u'',
             u'actor': u'jurgen.konig',
             u'time': u'2018-04-29T22:00:00+00:00',
             u'action': u'dossier-transition-resolve',
             u'review_state': u'dossier-state-resolved'},
            browser.json)

    @browsing
    def test_reactivate_via_restapi(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_manager = LockingResolveManager(self.resolvable_dossier)
        resolve_manager.resolve()
        self.assert_state('dossier-state-resolved', self.resolvable_dossier)

        with freeze(datetime(2018, 4, 30)):
            self.api_transition(
                self.resolvable_dossier, 'dossier-transition-reactivate', browser)

        self.assert_state('dossier-state-active', self.resolvable_dossier)
        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {u'title': u'dossier-state-active',
             u'comments': u'',
             u'actor': u'jurgen.konig',
             u'time': u'2018-04-29T22:00:00+00:00',
             u'action': u'dossier-transition-reactivate',
             u'review_state': u'dossier-state-active'},
            browser.json)

    @browsing
    def test_deactivate_via_restapi(self, browser):
        self.login(self.secretariat_user, browser)
        self.assert_state('dossier-state-active', self.resolvable_dossier)

        with freeze(datetime(2018, 4, 30)):
            self.api_transition(
                self.resolvable_dossier, 'dossier-transition-deactivate', browser)

        self.assert_state('dossier-state-inactive', self.resolvable_dossier)
        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {u'title': u'dossier-state-inactive',
             u'comments': u'',
             u'actor': u'jurgen.konig',
             u'time': u'2018-04-29T22:00:00+00:00',
             u'action': u'dossier-transition-deactivate',
             u'review_state': u'dossier-state-inactive'},
            browser.json)

    @browsing
    def test_activate_via_restapi(self, browser):
        self.login(self.secretariat_user, browser)
        self.assert_state('dossier-state-inactive', self.inactive_dossier)

        with freeze(datetime(2018, 4, 30)):
            self.api_transition(
                self.inactive_dossier, 'dossier-transition-activate', browser)

        self.assert_state('dossier-state-active', self.inactive_dossier)
        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {u'title': u'dossier-state-active',
             u'comments': u'',
             u'actor': u'jurgen.konig',
             u'time': u'2018-04-29T22:00:00+00:00',
             u'action': u'dossier-transition-activate',
             u'review_state': u'dossier-state-active'},
            browser.json)

    @browsing
    def test_offer_resolved_via_restapi_is_forbidden(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_manager = LockingResolveManager(self.resolvable_dossier)
        resolve_manager.resolve()
        self.assert_state('dossier-state-resolved', self.resolvable_dossier)

        self.login(self.records_manager, browser)
        browser.raise_http_errors = False
        self.api_transition(
            self.resolvable_dossier, 'dossier-transition-offer', browser)

        self.assert_state('dossier-state-resolved', self.resolvable_dossier)
        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'error':
                {u'message': u"Invalid transition 'dossier-transition-offer'.\nValid transitions are:\n",
                 u'type': u'Bad Request'}},
            browser.json)

    @browsing
    def test_offered_to_resolved_via_restapi_is_forbidden(self, browser):
        self.login(self.records_manager, browser)
        self.assert_state('dossier-state-offered', self.offered_dossier_to_archive)

        browser.raise_http_errors = False
        self.api_transition(self.offered_dossier_to_archive,
                            'dossier-transition-offered-to-resolved', browser)

        self.assert_state('dossier-state-offered', self.offered_dossier_to_archive)
        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'error':
                {u'message': u"Invalid transition 'dossier-transition-offered-to-resolved'.\nValid transitions are:\n",
                 u'type': u'Bad Request'}},
            browser.json)

    @browsing
    def test_offer_inactive_via_restapi_is_forbidden(self, browser):
        self.login(self.records_manager, browser)
        self.assert_state('dossier-state-inactive', self.inactive_dossier)

        browser.raise_http_errors = False
        self.api_transition(
            self.inactive_dossier, 'dossier-transition-offer', browser)

        self.assert_state('dossier-state-inactive', self.inactive_dossier)
        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'error':
                {u'message': u"Invalid transition 'dossier-transition-offer'.\nValid transitions are:\n",
                 u'type': u'Bad Request'}},
            browser.json)

    @browsing
    def test_offered_to_inactive_via_restapi_is_forbidden(self, browser):
        self.login(self.records_manager, browser)
        self.assert_state('dossier-state-offered', self.offered_dossier_to_archive)

        browser.raise_http_errors = False
        self.api_transition(self.offered_dossier_to_archive,
                            'dossier-transition-offered-to-inactive', browser)

        self.assert_state('dossier-state-offered', self.offered_dossier_to_archive)
        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'error':
                {u'message': u"Invalid transition 'dossier-transition-offered-to-inactive'.\nValid transitions are:\n",
                 u'type': u'Bad Request'}},
            browser.json)

    @browsing
    def test_archive_offered_via_restapi_is_forbidden(self, browser):
        self.login(self.records_manager, browser)
        self.assert_state('dossier-state-offered', self.offered_dossier_to_archive)

        browser.raise_http_errors = False
        self.api_transition(self.offered_dossier_to_archive,
                            'dossier-transition-archive', browser)

        self.assert_state('dossier-state-offered', self.offered_dossier_to_archive)
        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'error':
                {u'message': u"Invalid transition 'dossier-transition-archive'.\nValid transitions are:\n",
                 u'type': u'Bad Request'}},
            browser.json)
