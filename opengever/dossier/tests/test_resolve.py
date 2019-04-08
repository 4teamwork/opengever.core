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
from ftw.testbrowser.pages import editbar
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
from opengever.dossier.resolve_lock import ResolveLock
from opengever.ogds.base.utils import get_current_org_unit
from opengever.testing import IntegrationTestCase
from operator import itemgetter
from plone import api
from plone.app.testing import applyProfile
from plone.protect import createToken
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import pytz
import unittest


def get_resolver_vocabulary():
    voca_factory = getUtility(
        IVocabularyFactory,
        name='opengever.dossier.ValidResolverNamesVocabulary')
    return voca_factory(api.portal.get())


def resolve_dossier(dossier, browser):
    browser.open(dossier,
                 view='transition-resolve',
                 data={'_authenticator': createToken()})


class TestResolverVocabulary(IntegrationTestCase):

    def test_resolver_vocabulary(self):
        vocabulary = get_resolver_vocabulary()
        self.assertItemsEqual(
            [u'strict', u'lenient'],
            vocabulary.by_value.keys())


class TestResolvingDossiers(IntegrationTestCase):

    @browsing
    def test_archive_form_is_omitted_for_sites_without_filing_number_support(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_dossier(self.empty_dossier, browser)

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.empty_dossier))
        self.assertEquals(self.empty_dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has been succesfully resolved.'],
                          info_messages())

    @browsing
    def test_resolving_subdossier_when_parent_dossier_contains_documents(self, browser):
        self.login(self.secretariat_user, browser)

        create(Builder('document').within(self.subdossier))
        create(Builder('dossier').within(self.subdossier))

        resolve_dossier(self.subdossier, browser)

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.subdossier))
        statusmessages.assert_no_error_messages()
        self.assertEquals(
            ['The subdossier has been succesfully resolved.'],
            info_messages())

    @browsing
    def test_archive_form_is_omitted_when_resolving_subdossiers(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_dossier(self.subdossier, browser)

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.subdossier))
        self.assertEquals(self.subdossier.absolute_url(), browser.url)
        self.assertEquals(['The subdossier has been succesfully resolved.'],
                          info_messages())

    @browsing
    def test_cant_resolve_already_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        resolve_dossier(self.subdossier, browser)
        resolve_dossier(self.subdossier, browser)

        self.assertEquals(self.subdossier.absolute_url(), browser.url)
        self.assertEquals(['Dossier has already been resolved.'],
                          info_messages())


class TestResolveJobs(IntegrationTestCase):

    @browsing
    def test_all_trashed_documents_are_deleted_when_resolving_a_dossier_if_enabled(self, browser):
        self.activate_feature('purge-trash')
        self.login(self.secretariat_user, browser)

        doc1 = create(Builder('document').within(self.empty_dossier))
        doc2 = create(Builder('document').within(self.empty_dossier).trashed())

        with self.observe_children(self.empty_dossier) as children:
            resolve_dossier(self.empty_dossier, browser)

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
            resolve_dossier(self.empty_dossier, browser)

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

    @browsing
    def test_purging_trashed_documents_is_disabled_by_default(self, browser):
        self.login(self.secretariat_user, browser)
        doc1 = create(Builder('document').within(self.empty_dossier).trashed())

        with self.observe_children(self.empty_dossier) as children:
            resolve_dossier(self.empty_dossier, browser)

        self.assertIn(doc1, children['after'])

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
                    resolve_dossier(self.empty_dossier, browser)

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
                resolve_dossier(subdossier, browser)

        self.assertEquals(1, len(sub_children['added']))
        sub_journal_pdf, = sub_children['added']
        self.assertEqual(date(2016, 3, 15), sub_journal_pdf.document_date,
                         "End date should be set to dossier end date")

        with self.observe_children(self.empty_dossier) as main_children:
            with freeze(datetime(2016, 9, 1)):
                resolve_dossier(self.empty_dossier, browser)

        self.assertEquals(1, len(main_children['added']))
        main_journal_pdf, = main_children['added']
        self.assertEqual(date(2016, 3, 15), IDossier(self.empty_dossier).end,
                         "End should be earliest possible date")
        self.assertEqual(date(2016, 3, 15), main_journal_pdf.document_date,
                         "Document date should be earliest possible date")

    @browsing
    def test_journal_pdf_gets_updated_when_dossier_is_closed_again(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.secretariat_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            resolve_dossier(self.empty_dossier, browser)
        self.assertEquals(1, len(children['added']))
        journal_pdf, = children['added']
        self.assertEquals(0, journal_pdf.get_current_version_id(missing_as_zero=True))

        browser.open(self.empty_dossier, view='transition-reactivate', data={'_authenticator': createToken()})
        with self.observe_children(self.empty_dossier) as children:
            resolve_dossier(self.empty_dossier, browser)
        self.assertEquals(0, len(children['added']))
        self.assertEquals(1, journal_pdf.get_current_version_id(missing_as_zero=True))

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
                    resolve_dossier(self.empty_dossier, browser)

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

    @browsing
    def test_tasks_pdf_is_skipped_for_dossiers_without_tasks(self, browser):
        self.activate_feature('tasks-pdf')
        self.login(self.secretariat_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            resolve_dossier(self.empty_dossier, browser)

        self.assertEqual(0, len(children['added']))

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
                resolve_dossier(subdossier, browser)

        self.assertEquals(0, len(sub_children['added']))

        with self.observe_children(self.empty_dossier) as main_children:
            with freeze(datetime(2016, 9, 1)):
                resolve_dossier(self.empty_dossier, browser)

        self.assertEquals(1, len(main_children['added']))
        main_tasks_pdf, = main_children['added']
        self.assertEqual(date(2016, 3, 15), IDossier(self.empty_dossier).end,
                         "End should be earliest possible date")
        self.assertEqual(date(2016, 3, 15), main_tasks_pdf.document_date,
                         "Document date should be earliest possible date")

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
            resolve_dossier(self.empty_dossier, browser)
        self.assertEquals(1, len(children['added']))
        tasks_pdf, = children['added']
        tasks_pdf.reindexObject()
        self.assertEquals(0, tasks_pdf.get_current_version_id(missing_as_zero=True))

        browser.open(self.empty_dossier, view='transition-reactivate', data={'_authenticator': createToken()})
        with self.observe_children(self.empty_dossier) as children:
            resolve_dossier(self.empty_dossier, browser)
        self.assertEquals(0, len(children['added']))
        self.assertEquals(1, tasks_pdf.get_current_version_id(missing_as_zero=True))

    @browsing
    def test_tasks_and_journal_pdf_are_disabled_by_default(self, browser):
        self.login(self.secretariat_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            resolve_dossier(self.empty_dossier, browser)

        self.assertEquals(0, len(children['added']))

    @browsing
    def test_only_shadowed_documents_are_deleted_when_resolving_a_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        doc1 = create(Builder('document').within(self.empty_dossier))
        doc2 = create(Builder('document').within(self.empty_dossier).as_shadow_document())

        with self.observe_children(self.empty_dossier) as children:
            resolve_dossier(self.empty_dossier, browser)

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])

    @browsing
    def test_shadowed_documents_are_deleted_recursively_when_resolving_a_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        subdossier = create(Builder('dossier').within(self.empty_dossier))
        doc1 = create(Builder('document').within(subdossier))
        doc2 = create(Builder('document').within(subdossier).as_shadow_document())

        with self.observe_children(subdossier) as children:
            resolve_dossier(self.empty_dossier, browser)

        self.assertIn(doc1, children['after'])
        self.assertNotIn(doc2, children['after'])


class TestAutomaticPDFAConversion(IntegrationTestCase):

    def setUp(self):
        super(TestAutomaticPDFAConversion, self).setUp()
        reset_queue()

    def test_pdf_conversion_job_is_queued_for_every_document(self):
        self.activate_feature('bumblebee')
        self.login(self.secretariat_user)

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
            api.content.transition(obj=self.resolvable_dossier,
                                   transition='dossier-transition-resolve')

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

    def test_pdf_conversion_is_disabled_by_default(self):
        self.login(self.secretariat_user)
        get_queue().reset()

        with RequestsSessionMock.installed():
            api.content.transition(obj=self.resolvable_dossier,
                                   transition='dossier-transition-resolve')
            self.assertEquals(0, len(get_queue().queue))


class TestResolvingDossiersWithFilingNumberSupport(IntegrationTestCase):

    def setUp(self):
        super(TestResolvingDossiersWithFilingNumberSupport, self).setUp()
        applyProfile(self.portal, 'opengever.dossier:filing')

    @unittest.skip(
        "This test will fail until the redirect to the archive form is fixed "
        "(made to return an absolute instead of relative URL)"
    )
    @browsing
    def test_archive_form_is_displayed_for_sites_with_filing_number_support(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')
        self.assertEquals(
            '{}/transition-archive'.format(self.resolvable_dossier.absolute_url()),
            browser.url)


class TestResolveConditions(IntegrationTestCase):

    @browsing
    def test_resolving_is_cancelled_when_documents_are_not_filed_correctly(self, browser):
        self.login(self.secretariat_user, browser)

        create(Builder('document').within(self.resolvable_dossier))

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertTrue(self.resolvable_dossier.is_open())
        self.assertFalse(self.resolvable_dossier.is_resolved())
        self.assertEquals(self.resolvable_dossier.absolute_url(), browser.url)
        self.assertEquals(
            ['not all documents and tasks are stored in a subdossier.'],
            error_messages())

    @browsing
    def test_resolving_is_cancelled_when_documents_are_checked_out(self, browser):
        self.login(self.secretariat_user, browser)

        self.checkout_document(self.resolvable_document)

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertTrue(self.resolvable_dossier.is_open())
        self.assertFalse(self.resolvable_dossier.is_resolved())
        self.assertEquals(self.resolvable_dossier.absolute_url(), browser.url)
        self.assertEquals(['not all documents are checked in'],
                          error_messages())

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

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertTrue(self.resolvable_dossier.is_open())
        self.assertFalse(self.resolvable_dossier.is_resolved())
        self.assertEquals(self.resolvable_dossier.absolute_url(), browser.url)
        self.assertEquals(['not all task are closed'],
                          error_messages())

    @browsing
    def test_dossier_is_resolved_when_dossier_has_an_invalid_end_date(self, browser):
        self.login(self.secretariat_user, browser)

        IDossier(self.resolvable_dossier).end = date(1995, 1, 1)
        self.resolvable_dossier.reindexObject(idxs=['end'])

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertFalse(self.resolvable_dossier.is_open())
        self.assertTrue(self.resolvable_dossier.is_resolved())
        self.assertEquals(self.resolvable_dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has been succesfully resolved.'],
                          info_messages())

    @browsing
    def test_resolving_is_cancelled_when_subdossier_has_an_invalid_end_date(self, browser):
        self.login(self.secretariat_user, browser)

        IDossier(self.resolvable_subdossier).end = date(1995, 1, 1)
        self.resolvable_subdossier.reindexObject(idxs=['end'])

        IChanged(self.resolvable_document).changed = datetime(2016, 6, 1, tzinfo=pytz.utc)
        self.resolvable_document.reindexObject(idxs=['changed'])

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertTrue(self.resolvable_dossier.is_open())
        self.assertFalse(self.resolvable_dossier.is_resolved())
        self.assertEquals(self.resolvable_dossier.absolute_url(), browser.url)
        self.assertEquals(
            ['The dossier Resolvable Subdossier has a invalid end_date'],
            error_messages())

    @browsing
    def test_dossier_is_resolved_when_resolved_subdossier_has_an_invalid_end_date(self, browser):
        self.login(self.secretariat_user, browser)

        resolved_subdossier = create(Builder('dossier')
                                     .having(end=date(2016, 5, 7))
                                     .within(self.resolvable_dossier)
                                     .in_state('dossier-state-resolved'))
        with freeze(datetime(2016, 6, 1)):
            create(Builder('document').within(resolved_subdossier))

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertFalse(self.resolvable_dossier.is_open())
        self.assertTrue(self.resolvable_dossier.is_resolved())
        self.assertEquals(self.resolvable_dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has been succesfully resolved.'],
                          info_messages())

    @browsing
    def test_resolving_is_cancelled_when_dossier_has_active_proposals(self, browser):
        self.login(self.secretariat_user, browser)

        create(Builder('proposal').within(self.resolvable_subdossier))

        browser.open(self.resolvable_subdossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertTrue(self.resolvable_subdossier.is_open())
        self.assertFalse(self.resolvable_subdossier.is_resolved())
        self.assertEquals(self.resolvable_subdossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier contains active proposals.'],
                          error_messages())

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

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertFalse(self.resolvable_dossier.is_open())
        self.assertTrue(self.resolvable_dossier.is_resolved())
        self.assertEquals(self.resolvable_dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has been succesfully resolved.'],
                          info_messages())


class TestResolving(IntegrationTestCase):

    @browsing
    def test_set_end_date_to_earliest_possible_one(self, browser):
        self.login(self.secretariat_user, browser)

        IDossier(self.resolvable_dossier).start = date(2015, 1, 1)
        IDossier(self.resolvable_subdossier).start = date(2015, 1, 1)
        IChanged(self.resolvable_document).changed = datetime(2016, 6, 1, tzinfo=pytz.utc)
        self.resolvable_document.reindexObject(idxs=['changed'])

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertEquals(date(2016, 6, 1), IDossier(self.resolvable_dossier).end)
        self.assertEquals(date(2016, 6, 1), IDossier(self.resolvable_subdossier).end,
                          'The end date has not been set recursively.')

    @browsing
    def test_resolves_the_dossier_and_subdossiers(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.resolvable_dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.resolvable_subdossier))

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

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertEquals(self.resolvable_dossier.absolute_url(), browser.url)
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.resolvable_dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.resolvable_subdossier))
        self.assertEquals(
            ['The dossier has been succesfully resolved.'], info_messages())

    @browsing
    def test_handles_already_resolved_subdossiers(self, browser):
        self.login(self.secretariat_user, browser)

        create(Builder('dossier')
               .within(self.resolvable_dossier)
               .in_state('dossier-state-resolved'))

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.resolvable_dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.resolvable_subdossier))

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

        browser.open(self.empty_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.empty_dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(subdossier1))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(subdossier2))
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

        browser.open(self.resolvable_dossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.resolvable_dossier))
        self.assertEquals('dossier-state-inactive',
                          api.content.get_state(subdossier))

    @browsing
    def test_resolving_only_a_subdossier_is_possible(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.resolvable_subdossier,
                     {'_authenticator': createToken()},
                     view='transition-resolve')

        self.assertEquals('dossier-state-active',
                          api.content.get_state(self.resolvable_dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(self.resolvable_subdossier))


class TestResolvingReindexing(IntegrationTestCase):

    @browsing
    def test_end_date_is_reindexed(self, browser):
        self.login(self.secretariat_user, browser)
        enddate = datetime(2016, 8, 31)
        enddate_index_value = self.dateindex_value_from_datetime(enddate)

        browser.open(self.subsubdossier)
        editbar.menu_option('Actions', 'dossier-transition-resolve').click()
        self.assertEqual(enddate.date(), IDossier(self.subsubdossier).end)
        self.assert_index_value(enddate_index_value, 'end', self.subsubdossier)
        self.assert_metadata_value(enddate.date(), 'end', self.subsubdossier)


class TestResolveLocking(TestBylineBase):

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

        resolve_dossier(self.empty_dossier, browser)

        self.assertEquals(
            ['Dossier is already being resolved'], info_messages())

        self.assertEquals('dossier-state-active',
                          api.content.get_state(self.empty_dossier))
