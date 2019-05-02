from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests import RequestsSessionMock
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.bumblebee.tests.helpers import get_queue
from ftw.bumblebee.tests.helpers import reset_queue
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.base.behaviors.changed import IChanged
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.document.interfaces import IDossierJournalPDFMarker
from opengever.document.interfaces import IDossierTasksPDFMarker
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.dossier.nightly_after_resolve_job import ExecuteNightlyAfterResolveJobs
from opengever.dossier.resolve import AfterResolveJobs
from opengever.dossier.resolve_lock import ResolveLock
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import index_data_for
from operator import itemgetter
from plone import api
from plone.app.testing import applyProfile
from plone.protect import createToken
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import logging
import pytz


def get_resolver_vocabulary():
    voca_factory = getUtility(
        IVocabularyFactory,
        name='opengever.dossier.ValidResolverNamesVocabulary')
    return voca_factory(api.portal.get())


class ResolveTestHelper(object):

    resolved_state = 'dossier-state-resolved'
    inactive_state = 'dossier-state-inactive'

    def resolve(self, dossier, browser=None):
        return browser.open(dossier,
                            view='transition-resolve',
                            data={'_authenticator': createToken()})

    def reactivate(self, dossier, browser=None):
        return browser.open(dossier,
                            view='transition-reactivate',
                            data={'_authenticator': createToken()})

    def assert_success(self, dossier, browser, info_msgs=None):
        self.assertEquals(dossier.absolute_url(), browser.url)
        statusmessages.assert_no_error_messages()
        self.assertEquals(info_msgs, info_messages())

    def assert_errors(self, dossier, browser, error_msgs):
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(error_msgs, error_messages())

    def assert_already_resolved(self, dossier, browser):
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['Dossier has already been resolved.'],
                          info_messages())

    def assert_already_being_resolved(self, dossier, browser):
        self.assertEquals(
            ['Dossier is already being resolved'], info_messages())

    def assert_resolved(self, dossier):
        dossier_state = api.content.get_state(dossier)
        msg = ("Expected dossier %r to be resolved (state %r). "
               "Actual state is %r instead." % (
                   dossier, self.resolved_state, dossier_state))
        self.assertEquals(self.resolved_state, dossier_state, msg)

    def assert_not_resolved(self, dossier):
        dossier_state = api.content.get_state(dossier)
        msg = ("Expected dossier %r to NOT be resolved (NOT in state %r). "
               "Actual state is %r however." % (
                   dossier, self.resolved_state, dossier_state))
        self.assertNotEqual(self.resolved_state, dossier_state, msg)

    def assert_inactive(self, dossier):
        dossier_state = api.content.get_state(dossier)
        msg = ("Expected dossier %r to be inactive (state %r). "
               "Actual state is %r instead." % (
                   dossier, self.inactive_state, dossier_state))
        self.assertEquals(self.inactive_state, dossier_state, msg)


class ResolveTestHelperRESTAPI(ResolveTestHelper):
    """Implementation of the ResolveTestHelper for use with REST API.

    This helper resolves dossiers via REST API calls, and asserts on
    success / failure by looking at HTTP status codes and JSON content of
    the response.
    """

    api_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    def resolve(self, dossier, browser):
        browser.raise_http_errors = False
        url = dossier.absolute_url() + '/@workflow/dossier-transition-resolve'
        browser.open(
            url,
            method='POST',
            headers=self.api_headers)

    def assert_success(self, dossier, browser, info_msgs=None):
        self.assertEqual(200, browser.status_code)
        expected_url = dossier.absolute_url() + '/@workflow/dossier-transition-resolve'
        self.assertEquals(expected_url, browser.url)
        self.assertDictContainsSubset(
            {u'title': u'dossier-state-resolved',
             u'comments': u'',
             u'actor': api.user.get_current().getId(),
             u'action': u'dossier-transition-resolve',
             u'review_state': u'dossier-state-resolved'},
            browser.json)

    def assert_errors(self, dossier, browser, error_msgs):
        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'error': {
                u'message': u'',
                u'errors': error_msgs,
                u'type': u'PreconditionsViolated'}},
            browser.json)
        expected_url = dossier.absolute_url() + '/@workflow/dossier-transition-resolve'
        self.assertEquals(expected_url, browser.url)

    def assert_already_resolved(self, dossier, browser):
        self.assertEquals(400, browser.status_code)
        self.assertEquals(
            {u'error':
                {u'message': u'Dossier has already been resolved.',
                 u'type': u'Bad Request'}},
            browser.json)
        expected_url = dossier.absolute_url() + '/@workflow/dossier-transition-resolve'
        self.assertEquals(expected_url, browser.url)

    def assert_already_being_resolved(self, dossier, browser):
        self.assertEquals(400, browser.status_code)
        self.assertEquals({
            u'error': {
                u'message': u'Dossier is already being resolved',
                u'type': u'AlreadyBeingResolved'}},
            browser.json)


class TestResolverVocabulary(IntegrationTestCase):

    def test_resolver_vocabulary(self):
        vocabulary = get_resolver_vocabulary()
        self.assertItemsEqual(
            [u'strict', u'lenient'],
            vocabulary.by_value.keys())


class TestResolvingDossiers(IntegrationTestCase, ResolveTestHelper):

    @browsing
    def test_archive_form_is_omitted_for_sites_without_filing_number_support(self, browser):
        self.login(self.secretariat_user, browser)

        self.resolve(self.empty_dossier, browser)

        self.assert_resolved(self.empty_dossier)
        self.assert_success(self.empty_dossier, browser,
                            ['The dossier has been succesfully resolved.'])

    @browsing
    def test_resolving_subdossier_when_parent_dossier_contains_documents(self, browser):
        self.login(self.secretariat_user, browser)

        create(Builder('document').within(self.subdossier))
        create(Builder('dossier').within(self.subdossier))

        self.resolve(self.subdossier, browser)

        self.assert_resolved(self.subdossier)
        self.assert_success(self.subdossier, browser,
                            ['The subdossier has been succesfully resolved.'])

    @browsing
    def test_archive_form_is_omitted_when_resolving_subdossiers(self, browser):
        self.login(self.secretariat_user, browser)

        self.resolve(self.subdossier, browser)

        self.assert_resolved(self.subdossier)
        self.assert_success(self.subdossier, browser,
                            ['The subdossier has been succesfully resolved.'])

    @browsing
    def test_cant_resolve_already_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        self.resolve(self.subdossier, browser)
        self.resolve(self.subdossier, browser)

        self.assert_already_resolved(self.subdossier, browser)


class TestResolvingDossiersRESTAPI(ResolveTestHelperRESTAPI, TestResolvingDossiers):
    """Variant of the above test class to test dossier resolution via RESTAPI.
    """


class TestResolvingDossiersNightly(TestResolvingDossiers):
    """Variant of the above test class to test dossier resolution with the
    nightly jobs feature enabled.
    """

    features = ('nightly-jobs', )


class ResolveJobsTestHelper(object):
    """Helper to assert on the 'after_resolve_jobs_pending' flag's state
    in situations where after resolve jobs should have been executed.
    """

    def assert_after_resolve_jobs_pending(self, expected, dossiers):
        for dossier in dossiers:
            self.assertEqual(expected, AfterResolveJobs(dossier).after_resolve_jobs_pending)
            self.assertEqual(expected, index_data_for(dossier)['after_resolve_jobs_pending'])

    def assert_after_resolve_jobs_pending_in_expected_state(self, dossiers):
        self.assert_after_resolve_jobs_pending(False, dossiers)


class NightlyResolveJobsTestHelper(ResolveJobsTestHelper):
    """Helper to assert on the 'after_resolve_jobs_pending' flag's state
    in situations where after resolve jobs should NOT have been executed
    (i.e. when nightly jobs feature is enabled).
    """

    def assert_after_resolve_jobs_pending_in_expected_state(self, dossiers):
        self.assert_after_resolve_jobs_pending(True, dossiers)


class TestResolveJobs(IntegrationTestCase, ResolveTestHelper, ResolveJobsTestHelper):

    @browsing
    def test_all_trashed_documents_are_deleted_when_resolving_a_dossier_if_enabled(self, browser):
        self.activate_feature('purge-trash')
        self.login(self.secretariat_user, browser)

        doc1 = create(Builder('document').within(self.empty_dossier))
        doc2 = create(Builder('document').within(self.empty_dossier).trashed())

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier])

    @browsing
    def test_purge_trashs_recursive(self, browser):
        self.activate_feature('purge-trash')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier').within(self.empty_dossier))
        doc1 = create(Builder('document').within(subdossier))
        doc2 = create(Builder('document').within(subdossier).trashed())

        with self.observe_children(subdossier) as children:
            self.resolve(self.empty_dossier, browser)

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier, subdossier])

    @browsing
    def test_purging_trashed_documents_is_disabled_by_default(self, browser):
        self.login(self.secretariat_user, browser)
        doc1 = create(Builder('document').within(self.empty_dossier).trashed())

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        self.assertIn(doc1, children['after'])

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier])

    @browsing
    def test_adds_journal_pdf_to_main_and_subdossier(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier')
                            .within(self.empty_dossier)
                            .titled(u'Sub'))

        with self.observe_children(self.empty_dossier) as main_children:
            with self.observe_children(subdossier) as sub_children:
                with freeze(datetime(2016, 4, 25)):
                    self.resolve(self.empty_dossier, browser)

        self.assertEquals(1, len(main_children['added']))
        main_journal_pdf, = main_children['added']
        self.assertEquals(u'Journal of dossier An empty dossier, Apr 25, 2016 12:00 AM',
                          main_journal_pdf.title)
        self.assertEquals(u'Journal of dossier An empty dossier, Apr 25, 2016 12 00 AM.pdf',
                          main_journal_pdf.file.filename)
        self.assertEquals(u'application/pdf',
                          main_journal_pdf.file.contentType)
        self.assertTrue(IDossierJournalPDFMarker.providedBy(main_journal_pdf))
        self.assertFalse(main_journal_pdf.preserved_as_paper)

        self.assertEquals(1, len(sub_children['added']))
        sub_journal_pdf, = sub_children['added']
        self.assertEquals(u'Journal of dossier Sub, Apr 25, 2016 12:00 AM',
                          sub_journal_pdf.title)
        self.assertEquals(u'Journal of dossier Sub, Apr 25, 2016 12 00 AM.pdf',
                          sub_journal_pdf.file.filename)
        self.assertEquals(u'application/pdf',
                          sub_journal_pdf.file.contentType)
        self.assertTrue(IDossierJournalPDFMarker.providedBy(sub_journal_pdf))
        self.assertFalse(sub_journal_pdf.preserved_as_paper)

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier, subdossier])

    @browsing
    def test_sets_journal_pdf_document_date_to_dossier_end_date(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier')
                            .within(self.empty_dossier)
                            .having(
                                start=date(2016, 1, 1),
                                end=date(2016, 3, 15))
                            .titled(u'Sub'))

        with self.observe_children(subdossier) as sub_children:
            with freeze(datetime(2016, 4, 25)):
                self.resolve(subdossier, browser)

        self.assertEquals(1, len(sub_children['added']))
        sub_journal_pdf, = sub_children['added']
        self.assertEqual(date(2016, 3, 15), sub_journal_pdf.document_date,
                         "End date should be set to dossier end date")

        with self.observe_children(self.empty_dossier) as main_children:
            with freeze(datetime(2016, 9, 1)):
                self.resolve(self.empty_dossier, browser)

        self.assertEquals(1, len(main_children['added']))
        main_journal_pdf, = main_children['added']
        self.assertEqual(date(2016, 3, 15), IDossier(self.empty_dossier).end,
                         "End should be earliest possible date")
        self.assertEqual(date(2016, 3, 15), main_journal_pdf.document_date,
                         "Document date should be earliest possible date")

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier, subdossier])

    @browsing
    def test_journal_pdf_gets_updated_when_dossier_is_closed_again(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.secretariat_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)
        self.assertEquals(1, len(children['added']))
        journal_pdf, = children['added']
        self.assertEquals(0, journal_pdf.get_current_version_id(missing_as_zero=True))

        self.reactivate(self.empty_dossier, browser)
        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)
        self.assertEquals(0, len(children['added']))
        self.assertEquals(1, journal_pdf.get_current_version_id(missing_as_zero=True))

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier])

    @browsing
    def test_adds_tasks_pdf_only_to_main_dossier(self, browser):
        self.activate_feature('tasks-pdf')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier')
                            .within(self.empty_dossier)
                            .titled(u'Sub'))
        create(Builder('task')
               .within(subdossier)
               .titled(u'Arbeitsentwurf checken')
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-tested-and-closed'))

        with self.observe_children(self.empty_dossier) as main_children:
            with self.observe_children(subdossier) as sub_children:
                with freeze(datetime(2016, 4, 25)):
                    self.resolve(self.empty_dossier, browser)

        self.assertEquals(1, len(main_children['added']))
        main_tasks_pdf, = main_children['added']
        self.assertEquals(u'Task list of dossier An empty dossier, Apr 25, 2016 12:00 AM',
                          main_tasks_pdf.title)
        self.assertEquals(u'Task list of dossier An empty dossier, Apr 25, 2016 12 00 AM.pdf',
                          main_tasks_pdf.file.filename)
        self.assertEquals(u'application/pdf',
                          main_tasks_pdf.file.contentType)
        self.assertTrue(IDossierTasksPDFMarker.providedBy(main_tasks_pdf))
        self.assertFalse(main_tasks_pdf.preserved_as_paper)

        self.assertEquals(0, len(sub_children['added']))

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier, subdossier])

    @browsing
    def test_tasks_pdf_is_skipped_for_dossiers_without_tasks(self, browser):
        self.activate_feature('tasks-pdf')
        self.login(self.secretariat_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        self.assertEqual(0, len(children['added']))

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier])

    @browsing
    def test_sets_tasks_pdf_document_date_to_dossier_end_date(self, browser):
        """When the document date is not set to the dossiers end date the
        subdossier will be left in an inconsistent state. this will make
        resolving the main dossier impossible.
        """
        self.activate_feature('tasks-pdf')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier')
                            .within(self.empty_dossier)
                            .having(
                                start=date(2016, 1, 1),
                                end=date(2016, 3, 15))
                            .titled(u'Sub'))
        create(Builder('task')
               .within(subdossier)
               .titled(u'Arbeitsentwurf checken')
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-tested-and-closed'))

        with self.observe_children(subdossier) as sub_children:
            with freeze(datetime(2016, 4, 25)):
                self.resolve(subdossier, browser)

        self.assertEquals(0, len(sub_children['added']))

        with self.observe_children(self.empty_dossier) as main_children:
            with freeze(datetime(2016, 9, 1)):
                self.resolve(self.empty_dossier, browser)

        self.assertEquals(1, len(main_children['added']))
        main_tasks_pdf, = main_children['added']
        self.assertEqual(date(2016, 3, 15), IDossier(self.empty_dossier).end,
                         "End should be earliest possible date")
        self.assertEqual(date(2016, 3, 15), main_tasks_pdf.document_date,
                         "Document date should be earliest possible date")

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier, subdossier])

    @browsing
    def test_tasks_pdf_gets_updated_when_dossier_is_closed_again(self, browser):
        self.activate_feature('tasks-pdf')
        self.login(self.secretariat_user, browser)

        create(Builder('task')
               .within(self.empty_dossier)
               .titled(u'Arbeitsentwurf checken')
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-tested-and-closed'))

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)
        self.assertEquals(1, len(children['added']))
        tasks_pdf, = children['added']
        self.assertEquals(0, tasks_pdf.get_current_version_id(missing_as_zero=True))

        self.reactivate(self.empty_dossier, browser)
        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)
        self.assertEquals(0, len(children['added']))
        self.assertEquals(1, tasks_pdf.get_current_version_id(missing_as_zero=True))

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier])

    @browsing
    def test_tasks_and_journal_pdf_are_disabled_by_default(self, browser):
        self.login(self.secretariat_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        self.assertEquals(0, len(children['added']))

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier])

    @browsing
    def test_only_shadowed_documents_are_deleted_when_resolving_a_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        doc1 = create(Builder('document').within(self.empty_dossier))
        doc2 = create(Builder('document').within(self.empty_dossier).as_shadow_document())

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier])

    @browsing
    def test_shadowed_documents_are_deleted_recursively_when_resolving_a_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier').within(self.empty_dossier))
        doc1 = create(Builder('document').within(subdossier))
        doc2 = create(Builder('document').within(subdossier).as_shadow_document())

        with self.observe_children(subdossier) as children:
            self.resolve(self.empty_dossier, browser)

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending_in_expected_state(
            [self.empty_dossier, subdossier])


class TestResolveJobsRESTAPI(ResolveTestHelperRESTAPI, TestResolveJobs):
    """Variant of the above test class to test dossier resolution via RESTAPI.
    """


class TestResolveJobsNightly(NightlyResolveJobsTestHelper, TestResolveJobs):
    """Variant of the above test class to test dossier resolution with the
    nightly jobs feature enabled.

    These tests should test that the respective jobs are NOT executed when
    the nightly jobs feature is enabled, but produce the same result when
    the nightly job is triggered afterwards.

    They usually follow this pattern:
    - Resolve one or more dossiers
    - Assert that none of the work of the AfterResolveJobs has been done yet
    - Assert that the AfterResolveJobs are flagged as still pending
    - Run the nightly job(s)
    - Assert that the AfterResolveJobs work has been done
    - Assert that the AfterResolveJobs are not flagged as pending any more
    """

    features = ('nightly-jobs', )

    def interrupt_if_necessary(self):
        """Stub out the runner's `interrupt_if_necessary` function.
        """

    def execute_nightly_jobs(self, expected=None):
        """Run all pending after resolve nightly jobs, and assert on the
        number of jobs.
        """
        null_logger = logging.getLogger('opengever.nightlyjobs')
        null_logger.addHandler(logging.NullHandler())

        nightly_job_provider = ExecuteNightlyAfterResolveJobs(
            self.portal, self.request, null_logger)

        jobs = list(nightly_job_provider)
        if expected:
            self.assertEqual(expected, len(jobs))
            self.assertEqual(expected, len(nightly_job_provider))

        for job in jobs:
            nightly_job_provider.run_job(job, self.interrupt_if_necessary)

    @browsing
    def test_all_trashed_documents_are_deleted_when_resolving_a_dossier_if_enabled(self, browser):
        self.activate_feature('purge-trash')
        self.login(self.secretariat_user, browser)

        doc1 = create(Builder('document').within(self.empty_dossier))
        doc2 = create(Builder('document').within(self.empty_dossier).trashed())

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertIn(doc1, children['after'])
        self.assertIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as children:
            self.execute_nightly_jobs(expected=1)

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier])

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

    @browsing
    def test_purge_trashs_recursive(self, browser):
        self.activate_feature('purge-trash')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier').within(self.empty_dossier))
        doc1 = create(Builder('document').within(subdossier))
        doc2 = create(Builder('document').within(subdossier).trashed())

        with self.observe_children(subdossier) as children:
            self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertIn(doc1, children['after'])
        self.assertIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier, subdossier])

        # Now run the nightly jobs
        with self.observe_children(subdossier) as children:
            self.execute_nightly_jobs(expected=2)

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier, subdossier])

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

    @browsing
    def test_adds_journal_pdf_to_main_and_subdossier(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier')
                            .within(self.empty_dossier)
                            .titled(u'Sub'))

        with self.observe_children(self.empty_dossier) as main_children:
            with self.observe_children(subdossier) as sub_children:
                with freeze(datetime(2016, 4, 25)):
                    self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertEquals(0, len(main_children['added']))
        self.assertEquals(0, len(sub_children['added']))

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier, subdossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as main_children:
            with self.observe_children(subdossier) as sub_children:
                with freeze(datetime(2016, 4, 25)):
                    self.execute_nightly_jobs(expected=2)

        self.assertEquals(1, len(main_children['added']))
        main_journal_pdf, = main_children['added']
        self.assertEquals(u'Journal of dossier An empty dossier, Apr 25, 2016 12:00 AM',
                          main_journal_pdf.title)
        self.assertEquals(u'Journal of dossier An empty dossier, Apr 25, 2016 12 00 AM.pdf',
                          main_journal_pdf.file.filename)
        self.assertEquals(u'application/pdf',
                          main_journal_pdf.file.contentType)
        self.assertTrue(IDossierJournalPDFMarker.providedBy(main_journal_pdf))
        self.assertFalse(main_journal_pdf.preserved_as_paper)

        self.assertEquals(1, len(sub_children['added']))
        sub_journal_pdf, = sub_children['added']
        self.assertEquals(u'Journal of dossier Sub, Apr 25, 2016 12:00 AM',
                          sub_journal_pdf.title)
        self.assertEquals(u'Journal of dossier Sub, Apr 25, 2016 12 00 AM.pdf',
                          sub_journal_pdf.file.filename)
        self.assertEquals(u'application/pdf',
                          sub_journal_pdf.file.contentType)
        self.assertTrue(IDossierJournalPDFMarker.providedBy(sub_journal_pdf))
        self.assertFalse(sub_journal_pdf.preserved_as_paper)

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier, subdossier])

    @browsing
    def test_sets_journal_pdf_document_date_to_dossier_end_date(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier')
                            .within(self.empty_dossier)
                            .having(
                                start=date(2016, 1, 1),
                                end=date(2016, 3, 15))
                            .titled(u'Sub'))

        # Resolve subdossier
        with self.observe_children(subdossier) as sub_children:
            with freeze(datetime(2016, 4, 25)):
                self.resolve(subdossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertEquals(0, len(sub_children['added']))

        self.assert_after_resolve_jobs_pending(
            True, [subdossier])

        # Now run the nightly jobs
        with self.observe_children(subdossier) as sub_children:
            with freeze(datetime(2016, 4, 25)):
                self.execute_nightly_jobs(expected=1)

        self.assertEquals(1, len(sub_children['added']))
        sub_journal_pdf, = sub_children['added']
        self.assertEqual(date(2016, 3, 15), sub_journal_pdf.document_date,
                         "End date should be set to dossier end date")

        self.assert_after_resolve_jobs_pending(
            False, [subdossier])

        # Resolve main dossier
        with self.observe_children(self.empty_dossier) as main_children:
            with freeze(datetime(2016, 9, 1)):
                self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertEquals(0, len(main_children['added']))

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as main_children:
            with freeze(datetime(2016, 4, 25)):
                self.execute_nightly_jobs(expected=1)

        self.assertEquals(1, len(main_children['added']))
        main_journal_pdf, = main_children['added']
        self.assertEqual(date(2016, 3, 15), IDossier(self.empty_dossier).end,
                         "End should be earliest possible date")
        self.assertEqual(date(2016, 3, 15), main_journal_pdf.document_date,
                         "Document date should be earliest possible date")

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier])

    @browsing
    def test_journal_pdf_gets_updated_when_dossier_is_closed_again(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.secretariat_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertEquals(0, len(children['added']))

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as children:
                self.execute_nightly_jobs(expected=1)

        self.assertEquals(1, len(children['added']))
        journal_pdf, = children['added']
        self.assertEquals(0, journal_pdf.get_current_version_id(missing_as_zero=True))

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier])

        # Now reactivate and close the dossier again
        self.reactivate(self.empty_dossier, browser)
        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertEquals(0, len(children['added']))
        self.assertEquals(0, journal_pdf.get_current_version_id(missing_as_zero=True))

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as children:
                self.execute_nightly_jobs(expected=1)

        self.assertEquals(0, len(children['added']))
        self.assertEquals(1, journal_pdf.get_current_version_id(missing_as_zero=True))

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier])

    @browsing
    def test_adds_tasks_pdf_only_to_main_dossier(self, browser):
        self.activate_feature('tasks-pdf')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier')
                            .within(self.empty_dossier)
                            .titled(u'Sub'))
        create(Builder('task')
               .within(subdossier)
               .titled(u'Arbeitsentwurf checken')
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-tested-and-closed'))

        with self.observe_children(self.empty_dossier) as main_children:
            with self.observe_children(subdossier) as sub_children:
                with freeze(datetime(2016, 4, 25)):
                    self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertEquals(0, len(main_children['added']))
        self.assertEquals(0, len(sub_children['added']))

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier, subdossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as main_children:
            with self.observe_children(subdossier) as sub_children:
                with freeze(datetime(2016, 4, 25)):
                    self.execute_nightly_jobs(expected=2)

        self.assertEquals(1, len(main_children['added']))
        main_tasks_pdf, = main_children['added']
        self.assertEquals(u'Task list of dossier An empty dossier, Apr 25, 2016 12:00 AM',
                          main_tasks_pdf.title)
        self.assertEquals(u'Task list of dossier An empty dossier, Apr 25, 2016 12 00 AM.pdf',
                          main_tasks_pdf.file.filename)
        self.assertEquals(u'application/pdf',
                          main_tasks_pdf.file.contentType)
        self.assertTrue(IDossierTasksPDFMarker.providedBy(main_tasks_pdf))
        self.assertFalse(main_tasks_pdf.preserved_as_paper)

        self.assertEquals(0, len(sub_children['added']))

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier, subdossier])

    @browsing
    def test_tasks_pdf_is_skipped_for_dossiers_without_tasks(self, browser):
        self.activate_feature('tasks-pdf')
        self.login(self.secretariat_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)
            self.execute_nightly_jobs(expected=1)

        self.assertEqual(0, len(children['added']))

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier])

    @browsing
    def test_sets_tasks_pdf_document_date_to_dossier_end_date(self, browser):
        """When the document date is not set to the dossiers end date the
        subdossier will be left in an inconsistent state. this will make
        resolving the main dossier impossible.
        """
        self.activate_feature('tasks-pdf')
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier')
                            .within(self.empty_dossier)
                            .having(
                                start=date(2016, 1, 1),
                                end=date(2016, 3, 15))
                            .titled(u'Sub'))
        create(Builder('task')
               .within(subdossier)
               .titled(u'Arbeitsentwurf checken')
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-tested-and-closed'))

        with self.observe_children(subdossier) as sub_children:
            with freeze(datetime(2016, 4, 25)):
                self.resolve(subdossier, browser)
                self.execute_nightly_jobs(expected=1)

        self.assertEquals(0, len(sub_children['added']))

        with self.observe_children(self.empty_dossier) as main_children:
            with freeze(datetime(2016, 9, 1)):
                self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertEquals(0, len(main_children['added']))

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as main_children:
            with freeze(datetime(2016, 9, 1)):
                self.execute_nightly_jobs(expected=1)

        self.assertEquals(1, len(main_children['added']))
        main_tasks_pdf, = main_children['added']
        self.assertEqual(date(2016, 3, 15), IDossier(self.empty_dossier).end,
                         "End should be earliest possible date")
        self.assertEqual(date(2016, 3, 15), main_tasks_pdf.document_date,
                         "Document date should be earliest possible date")

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier])

    @browsing
    def test_tasks_pdf_gets_updated_when_dossier_is_closed_again(self, browser):
        self.activate_feature('tasks-pdf')
        self.login(self.secretariat_user, browser)

        create(Builder('task')
               .within(self.empty_dossier)
               .titled(u'Arbeitsentwurf checken')
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-tested-and-closed'))

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertEquals(0, len(children['added']))

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as children:
            self.execute_nightly_jobs(expected=1)

        self.assertEquals(1, len(children['added']))
        tasks_pdf, = children['added']
        self.assertEquals(0, tasks_pdf.get_current_version_id(missing_as_zero=True))

        # Now reactivate and close the dossier again
        self.reactivate(self.empty_dossier, browser)
        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertEquals(0, len(children['added']))
        self.assertEquals(0, tasks_pdf.get_current_version_id(missing_as_zero=True))

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as children:
            self.execute_nightly_jobs(expected=1)

        self.assertEquals(0, len(children['added']))
        self.assertEquals(1, tasks_pdf.get_current_version_id(missing_as_zero=True))

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier])

    @browsing
    def test_only_shadowed_documents_are_deleted_when_resolving_a_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        doc1 = create(Builder('document').within(self.empty_dossier))
        doc2 = create(Builder('document').within(self.empty_dossier).as_shadow_document())

        with self.observe_children(self.empty_dossier) as children:
            self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertIn(doc1, children['after'])
        self.assertIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.empty_dossier) as children:
            self.execute_nightly_jobs(expected=1)

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier])

    @browsing
    def test_shadowed_documents_are_deleted_recursively_when_resolving_a_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier').within(self.empty_dossier))
        doc1 = create(Builder('document').within(subdossier))
        doc2 = create(Builder('document').within(subdossier).as_shadow_document())

        with self.observe_children(subdossier) as children:
            self.resolve(self.empty_dossier, browser)

        # Nothing happened yet, resolve jobs still flagged as pending
        self.assertIn(doc1, children['after'])
        self.assertIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending(
            True, [self.empty_dossier, subdossier])

        # Now run the nightly jobs
        with self.observe_children(subdossier) as children:
            self.execute_nightly_jobs(expected=2)

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

        self.assert_after_resolve_jobs_pending(
            False, [self.empty_dossier, subdossier])


class TestAutomaticPDFAConversion(IntegrationTestCase, ResolveTestHelper):

    def setUp(self):
        super(TestAutomaticPDFAConversion, self).setUp()
        reset_queue()

    @browsing
    def test_pdf_conversion_job_is_queued_for_every_document(self, browser):
        self.activate_feature('bumblebee')
        self.login(self.secretariat_user, browser)

        api.portal.set_registry_record(
            'archival_file_conversion_enabled', True,
            interface=IDossierResolveProperties)

        doc1 = create(Builder('document')
                      .within(self.resolvable_subdossier)
                      .attach_file_containing(
                          bumblebee_asset('example.docx').bytes(),
                          u'example.docx'))

        get_queue().reset()
        with RequestsSessionMock.installed():
            self.resolve(self.resolvable_dossier, browser)
            self.assertEquals(2, len(get_queue().queue))
            queue_contents = list(get_queue().queue)
            queue_contents.sort(key=itemgetter('url'))

            fixture_doc_job = queue_contents[0]
            additional_doc_job = queue_contents[1]

            self.assertDictContainsSubset(
                {'callback_url': '{}/archival_file_conversion_callback'.format(
                    self.resolvable_document.absolute_url()),
                 'file_url': 'http://nohost/plone/bumblebee_download?checksum={}&uuid={}'.format(
                     DOCX_CHECKSUM, IUUID(self.resolvable_document)),
                 'target_format': 'pdf/a',
                 'url': '{}/bumblebee_trigger_conversion'.format(self.resolvable_document.absolute_url_path())},
                fixture_doc_job)

            self.assertDictContainsSubset(
                {'callback_url': '{}/archival_file_conversion_callback'.format(
                    doc1.absolute_url()),
                 'file_url': 'http://nohost/plone/bumblebee_download?checksum={}&uuid={}'.format(
                     DOCX_CHECKSUM, IUUID(doc1)),
                 'target_format': 'pdf/a',
                 'url': '{}/bumblebee_trigger_conversion'.format(doc1.absolute_url_path())},
                additional_doc_job)

    @browsing
    def test_pdf_conversion_is_disabled_by_default(self, browser):
        self.login(self.secretariat_user, browser)
        get_queue().reset()

        with RequestsSessionMock.installed():
            self.resolve(self.resolvable_dossier, browser)
            self.assertEquals(0, len(get_queue().queue))


class TestAutomaticPDFAConversionRESTAPI(ResolveTestHelperRESTAPI, TestAutomaticPDFAConversion):

    pass


class TestResolvingDossiersWithFilingNumberSupport(IntegrationTestCase, ResolveTestHelper):

    def setUp(self):
        super(TestResolvingDossiersWithFilingNumberSupport, self).setUp()
        applyProfile(self.portal, 'opengever.dossier:filing')

    @browsing
    def test_archive_form_is_displayed_for_sites_with_filing_number_support(self, browser):
        self.login(self.secretariat_user, browser)

        self.resolve(self.resolvable_dossier, browser)
        self.assertEquals(
            '{}/transition-archive'.format(self.resolvable_dossier.absolute_url()),
            browser.url)


class TestResolvingDossiersWithFilingNumberSupportRESTAPI(ResolveTestHelperRESTAPI, TestResolvingDossiersWithFilingNumberSupport):  # noqa

    @browsing
    def test_archive_form_is_displayed_for_sites_with_filing_number_support(self, browser):
        """Resolving dossiers via REST API with the filing number feature
        activated is currently not supported.
        """
        self.login(self.secretariat_user, browser)

        self.resolve(self.resolvable_dossier, browser)

        self.assertEqual(400, browser.status_code)
        self.assertEqual({
            u'error': {
                u'message': u"Can't resolve dossiers via REST API if filing number feature is activated",
                u'type': u'Bad Request'}},
            browser.json)

        self.assert_not_resolved(self.resolvable_dossier)


class TestResolveConditions(IntegrationTestCase, ResolveTestHelper):

    @browsing
    def test_resolving_is_cancelled_when_documents_are_not_filed_correctly(self, browser):
        self.login(self.secretariat_user, browser)

        create(Builder('document').within(self.resolvable_dossier))

        self.resolve(self.resolvable_dossier, browser)

        self.assert_not_resolved(self.resolvable_dossier)
        self.assert_errors(self.resolvable_dossier, browser,
                           ['not all documents and tasks are stored in a subdossier.'])

    @browsing
    def test_resolving_is_cancelled_when_documents_are_checked_out(self, browser):
        self.login(self.secretariat_user, browser)

        self.checkout_document(self.resolvable_document)

        self.resolve(self.resolvable_dossier, browser)

        self.assert_not_resolved(self.resolvable_dossier)
        self.assert_errors(self.resolvable_dossier, browser,
                           ['not all documents are checked in'])

    @browsing
    def test_resolving_is_cancelled_when_active_tasks_exist(self, browser):
        self.login(self.secretariat_user, browser)

        create(Builder('task')
               .within(self.resolvable_subdossier)
               .having(
                   responsible=self.regular_user.getId(),
                   responsible_client='fa',
                   issuer=self.dossier_responsible.getId(),
        ))

        self.resolve(self.resolvable_dossier, browser)

        self.assert_not_resolved(self.resolvable_dossier)
        self.assert_errors(self.resolvable_dossier, browser,
                           ['not all task are closed'])

    @browsing
    def test_dossier_is_resolved_when_dossier_has_an_invalid_end_date(self, browser):
        self.login(self.secretariat_user, browser)

        IDossier(self.resolvable_dossier).end = date(1995, 1, 1)
        self.resolvable_dossier.reindexObject(idxs=['end'])

        self.resolve(self.resolvable_dossier, browser)

        self.assert_resolved(self.resolvable_dossier)
        self.assert_success(self.resolvable_dossier, browser,
                            ['The dossier has been succesfully resolved.'])

    @browsing
    def test_resolving_is_cancelled_when_subdossier_has_an_invalid_end_date(self, browser):
        self.login(self.secretariat_user, browser)

        IDossier(self.resolvable_subdossier).end = date(1995, 1, 1)
        self.resolvable_subdossier.reindexObject(idxs=['end'])

        IChanged(self.resolvable_document).changed = datetime(2016, 6, 1, tzinfo=pytz.utc)
        self.resolvable_document.reindexObject(idxs=['changed'])

        self.resolve(self.resolvable_dossier, browser)

        self.assert_not_resolved(self.resolvable_dossier)
        self.assert_errors(self.resolvable_dossier, browser,
                           ['The dossier Resolvable Subdossier has a invalid end_date'])

    @browsing
    def test_dossier_is_resolved_when_resolved_subdossier_has_an_invalid_end_date(self, browser):
        self.login(self.secretariat_user, browser)

        resolved_subdossier = create(Builder('dossier')
                                     .having(end=date(2016, 5, 7))
                                     .within(self.resolvable_dossier)
                                     .in_state('dossier-state-resolved'))
        with freeze(datetime(2016, 6, 1)):
            create(Builder('document').within(resolved_subdossier))

        self.resolve(self.resolvable_dossier, browser)

        self.assert_resolved(self.resolvable_dossier)
        self.assert_success(self.resolvable_dossier, browser,
                            ['The dossier has been succesfully resolved.'])

    @browsing
    def test_resolving_is_cancelled_when_dossier_has_active_proposals(self, browser):
        self.login(self.secretariat_user, browser)

        create(Builder('proposal').within(self.resolvable_subdossier))

        self.resolve(self.resolvable_subdossier, browser)

        self.assert_not_resolved(self.resolvable_subdossier)
        self.assert_errors(self.resolvable_subdossier, browser,
                           ['The dossier contains active proposals.'])

    @browsing
    def test_dossier_is_resolved_when_all_tasks_are_closed_and_documents_checked_in(self, browser):
        self.login(self.secretariat_user, browser)

        self.assertFalse(self.resolvable_document.is_checked_out())
        create(Builder('task')
               .within(self.resolvable_subdossier)
               .in_state('task-state-tested-and-closed')
               .having(
                   responsible=self.regular_user.getId(),
                   responsible_client='fa',
                   issuer=self.dossier_responsible.getId(),
        ))

        self.resolve(self.resolvable_dossier, browser)

        self.assert_resolved(self.resolvable_dossier)
        self.assert_success(self.resolvable_dossier, browser,
                            ['The dossier has been succesfully resolved.'])


class TestResolveConditionsRESTAPI(ResolveTestHelperRESTAPI, TestResolveConditions):

    pass


class TestResolving(IntegrationTestCase, ResolveTestHelper):

    @browsing
    def test_set_end_date_to_earliest_possible_one(self, browser):
        self.login(self.secretariat_user, browser)

        IDossier(self.resolvable_dossier).start = date(2015, 1, 1)
        IDossier(self.resolvable_subdossier).start = date(2015, 1, 1)
        IChanged(self.resolvable_document).changed = datetime(2016, 6, 1, tzinfo=pytz.utc)
        self.resolvable_document.reindexObject(idxs=['changed'])

        self.resolve(self.resolvable_dossier, browser)

        self.assertEquals(date(2016, 6, 1), IDossier(self.resolvable_dossier).end)
        self.assertEquals(date(2016, 6, 1), IDossier(self.resolvable_subdossier).end,
                          'The end date has not been set recursively.')

    @browsing
    def test_resolves_the_dossier_and_subdossiers(self, browser):
        self.login(self.secretariat_user, browser)

        self.resolve(self.resolvable_dossier, browser)

        self.assert_resolved(self.resolvable_dossier)
        self.assert_resolved(self.resolvable_subdossier)

    @browsing
    def test_lenient_resolver_skips_document_and_task_filing_check(self, browser):
        self.login(self.secretariat_user, browser)

        api.portal.set_registry_record(
            'resolver_name', 'lenient', IDossierResolveProperties)

        create(Builder('document').within(self.resolvable_dossier))
        create(Builder('mail').within(self.resolvable_dossier))
        create(Builder('task')
               .within(self.resolvable_dossier)
               .in_state('task-state-tested-and-closed')
               .having(
                   responsible=self.regular_user.getId(),
                   responsible_client='fa',
                   issuer=self.dossier_responsible.getId(),
        ))

        self.resolve(self.resolvable_dossier, browser)

        self.assert_resolved(self.resolvable_dossier)
        self.assert_resolved(self.resolvable_subdossier)
        self.assert_success(self.resolvable_dossier, browser,
                            ['The dossier has been succesfully resolved.'])

    @browsing
    def test_handles_already_resolved_subdossiers(self, browser):
        self.login(self.secretariat_user, browser)

        create(Builder('dossier')
               .within(self.resolvable_dossier)
               .in_state('dossier-state-resolved'))

        self.resolve(self.resolvable_dossier, browser)

        self.assert_resolved(self.resolvable_dossier)
        self.assert_resolved(self.resolvable_subdossier)

    @browsing
    def test_corrects_already_resolved_subdossiers_invalid_end_dates(self, browser):
        """Invalid end date of resolved subdossier is automatically set to
        the earliest_possible_end_date of that subdossier, whereas end date
        of open subdossier is set to end_date of main dossier.
        """
        self.login(self.secretariat_user, browser)

        with freeze(datetime(2016, 5, 1)):
            subdossier1 = create(Builder('dossier')
                                 .within(self.empty_dossier)
                                 .having(end=date(2016, 5, 7))
                                 .in_state('dossier-state-resolved'))
            subdossier2 = create(Builder('dossier')
                                 .within(self.empty_dossier)
                                 .having(end=date(2016, 7, 1))
                                 .in_state('dossier-state-resolved'))
            subdossier3 = create(Builder('dossier')
                                 .within(self.empty_dossier)
                                 .having(end=date(2016, 5, 3)))
        with freeze(datetime(2016, 6, 1)):
            create(Builder('document').within(subdossier1))

        IDossier(self.empty_dossier).end = None
        self.assertEquals(None, IDossier(self.empty_dossier).end)
        self.assertEquals(date(2016, 5, 7), IDossier(subdossier1).end)
        self.assertEquals(date(2016, 7, 1), IDossier(subdossier2).end)
        self.assertEquals(date(2016, 5, 3), IDossier(subdossier3).end)

        self.resolve(self.empty_dossier, browser)

        self.assert_resolved(self.empty_dossier)
        self.assert_resolved(subdossier1)
        self.assert_resolved(subdossier2)
        self.assertEquals(date(2016, 7, 1), IDossier(self.empty_dossier).end)
        self.assertEquals(date(2016, 6, 1), IDossier(subdossier1).end)
        self.assertEquals(date(2016, 7, 1), IDossier(subdossier2).end)
        self.assertEquals(date(2016, 7, 1), IDossier(subdossier2).end)

    @browsing
    def test_inactive_subdossiers_stays_inactive(self, browser):
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier')
                            .within(self.resolvable_dossier)
                            .in_state('dossier-state-inactive'))

        self.resolve(self.resolvable_dossier, browser)

        self.assert_resolved(self.resolvable_dossier)
        self.assert_inactive(subdossier)

    @browsing
    def test_resolving_only_a_subdossier_is_possible(self, browser):
        self.login(self.secretariat_user, browser)

        self.resolve(self.resolvable_subdossier, browser)

        self.assert_not_resolved(self.resolvable_dossier)
        self.assert_resolved(self.resolvable_subdossier)


class TestResolvingRESTAPI(ResolveTestHelperRESTAPI, TestResolving):

    pass


class TestResolvingReindexing(IntegrationTestCase, ResolveTestHelper):

    @browsing
    def test_end_date_is_reindexed(self, browser):
        self.login(self.secretariat_user, browser)
        enddate = datetime(2016, 8, 31)
        enddate_index_value = self.dateindex_value_from_datetime(enddate)

        self.resolve(self.subsubdossier, browser)

        self.assertEqual(enddate.date(), IDossier(self.subsubdossier).end)
        self.assert_index_value(enddate_index_value, 'end', self.subsubdossier)
        self.assert_metadata_value(enddate.date(), 'end', self.subsubdossier)


class TestResolvingReindexingRESTAPI(ResolveTestHelperRESTAPI, TestResolvingReindexing):

    pass


class TestResolveLocking(TestBylineBase, ResolveTestHelper):

    @browsing
    def test_resolve_locked_dossier_is_recognized_as_such(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_lock = ResolveLock(self.empty_dossier)
        resolve_lock.acquire(commit=False)

        self.assertTrue(resolve_lock.is_locked())

        browser.open(self.empty_dossier)

        wfstate = self.get_byline_value_by_label('State:').text
        self.assertEqual('dossier-state-active (currently being resolved)', wfstate)

    @browsing
    def test_expired_resolve_lock_is_recognized(self, browser):
        self.login(self.secretariat_user, browser)

        with freeze(datetime(2018, 4, 30)) as freezer:
            resolve_lock = ResolveLock(self.empty_dossier)
            resolve_lock.acquire(commit=False)

            self.assertTrue(resolve_lock.is_locked())

            freezer.forward(hours=25)
            self.assertFalse(resolve_lock.is_locked())

    @browsing
    def test_resolve_lock_works_recursively_for_whole_subtree(self, browser):
        self.login(self.secretariat_user, browser)

        main_dossier = self.subdossier.aq_parent

        # Issue lock on the main dossier
        resolve_lock = ResolveLock(main_dossier)
        resolve_lock.acquire(commit=False)

        # Subdossier should also be considered locked
        self.assertTrue(ResolveLock(self.subdossier).is_locked())

        # Except if we explicitly check with recursive=False
        # (used for low-cost display in byline on every view)
        self.assertFalse(ResolveLock(self.subdossier).is_locked(recursive=False))

    @browsing
    def test_locked_dossier_cant_be_resolved(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_lock = ResolveLock(self.empty_dossier)
        resolve_lock.acquire(commit=False)

        self.resolve(self.empty_dossier, browser)

        self.assert_already_being_resolved(self.empty_dossier, browser)
        self.assertEquals('dossier-state-active',
                          api.content.get_state(self.empty_dossier))


class TestResolveLockingRESTAPI(ResolveTestHelperRESTAPI, TestResolveLocking):

    pass
