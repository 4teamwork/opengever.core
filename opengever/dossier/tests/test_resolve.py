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
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import applyProfile
from plone.protect import createToken
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import transaction


def get_resolver_vocabulary():
    voca_factory = getUtility(
        IVocabularyFactory,
        name='opengever.dossier.ValidResolverNamesVocabulary')
    return voca_factory(api.portal.get())


def resolve_dossier(dossier, browser):
    browser.open(dossier,
                 view='transition-resolve',
                 data={'_authenticator': createToken()})


class TestResolverVocabulary(FunctionalTestCase):

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
        self.assertFalse(main_journal_pdf.preserved_as_paper)

        self.assertEquals(1, len(sub_children['added']))
        sub_journal_pdf, = sub_children['added']
        self.assertEquals(u'Journal of dossier Sub, Apr 25, 2016 12:00 AM',
                          sub_journal_pdf.title)
        self.assertEquals(u'Journal of dossier Sub, Apr 25, 2016 12 00 AM.pdf',
                          sub_journal_pdf.file.filename)
        self.assertEquals(u'application/pdf',
                          sub_journal_pdf.file.contentType)
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

        # object provides index needs to be up to date for dossier resolving
        sub_journal_pdf.reindexObject(idxs=["object_provides"])
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
        journal_pdf.reindexObject()
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
        self.assertFalse(main_tasks_pdf.preserved_as_paper)

        self.assertEquals(0, len(sub_children['added']))

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


class TestAutomaticPDFAConversion(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestAutomaticPDFAConversion, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.grant('Contributor', 'Editor', 'Reader', 'Reviewer')
        self.catalog = api.portal.get_tool('portal_catalog')

        reset_queue()

    def test_pdf_conversion_job_is_queued_for_every_document(self):
        api.portal.set_registry_record(
            'archival_file_conversion_enabled', True,
            interface=IDossierResolveProperties)

        doc1 = create(Builder('document')
                      .within(self.dossier)
                      .attach_file_containing(
                          bumblebee_asset('example.docx').bytes(),
                          u'example.docx'))
        create(Builder('document')
               .within(self.dossier)
               .attach_file_containing(
                   bumblebee_asset('example.docx').bytes(),
                   u'example.docx'))

        get_queue().reset()
        with RequestsSessionMock.installed():
            api.content.transition(obj=self.dossier,
                                   transition='dossier-transition-resolve')
            transaction.commit()

            self.assertEquals(2, len(get_queue().queue))
            self.assertDictContainsSubset(
                {'callback_url': '{}/archival_file_conversion_callback'.format(
                    doc1.absolute_url()),
                 'file_url': 'http://nohost/plone/bumblebee_download?checksum={}&uuid={}'.format(
                     DOCX_CHECKSUM, IUUID(doc1)),
                 'target_format': 'pdf/a',
                 'url': '/plone/dossier-1/document-1/bumblebee_trigger_conversion'},
                get_queue().queue[0])

    def test_pdf_conversion_is_disabled_by_default(self):
        create(Builder('document')
               .within(self.dossier)
               .attach_file_containing(
                   bumblebee_asset('example.docx').bytes(),
                   u'example.docx'))

        get_queue().reset()

        with RequestsSessionMock.installed():
            api.content.transition(obj=self.dossier,
                                   transition='dossier-transition-resolve')
            transaction.commit()

            self.assertEquals(0, len(get_queue().queue))


class TestResolvingDossiersWithFilingNumberSupport(FunctionalTestCase):

    def setUp(self):
        super(TestResolvingDossiersWithFilingNumberSupport, self).setUp()

        applyProfile(self.portal, 'opengever.dossier:filing')

    @browsing
    def test_archive_form_is_displayed_for_sites_with_filing_number_support(self, browser):
        dossier = create(Builder('dossier')
                         .having(start=date(2013, 11, 5)))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')
        self.assertEquals(
            '{}/transition-archive'.format(dossier.absolute_url()),
            browser.url)


class TestResolveConditions(FunctionalTestCase):

    def setUp(self):
        super(TestResolveConditions, self).setUp()
        self.grant('Contributor', 'Editor', 'Reader', 'Reviewer')

    @browsing
    def test_resolving_is_cancelled_when_documents_are_not_filed_correctly(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('dossier').within(dossier))
        create(Builder('document').within(dossier).checked_out())

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertTrue(dossier.is_open())
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(
            ['not all documents and tasks are stored in a subdossier.',
             'not all documents are checked in'], error_messages())

    @browsing
    def test_resolving_is_cancelled_when_documents_are_checked_out(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('document').within(dossier).checked_out())

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertTrue(dossier.is_open())
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['not all documents are checked in'],
                          error_messages())

    @browsing
    def test_resolving_is_cancelled_when_active_tasks_exist(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('task').within(dossier))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertTrue(dossier.is_open())
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['not all task are closed'],
                          error_messages())

    @browsing
    def test_dossier_is_resolved_when_dossier_has_an_invalid_end_date(self, browser):
        dossier = create(Builder('dossier').having(end=date(2016, 5, 7)))
        with freeze(datetime(2016, 6, 1)):
            create(Builder('document').within(dossier))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertFalse(dossier.is_open())
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has been succesfully resolved.'],
                          info_messages())

    @browsing
    def test_resolving_is_cancelled_when_subdossier_has_an_invalid_end_date(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier')
                            .having(end=date(2016, 5, 7))
                            .within(dossier))
        with freeze(datetime(2016, 6, 1)):
            create(Builder('document').within(subdossier))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertTrue(dossier.is_open())
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has a invalid end_date'], error_messages())

    @browsing
    def test_resolving_is_cancelled_when_dossier_has_active_proposals(self, browser):
        repo = create(Builder('repository'))
        dossier = create(Builder('dossier')
                         .within(repo)
                         .having(end=date(2016, 5, 7)))
        create(Builder('proposal').within(dossier))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertTrue(dossier.is_open())
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier contains active proposals.'],
                          error_messages())

    @browsing
    def test_dossier_is_resolved_when_all_tasks_are_closed_and_documents_checked_in(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('document').within(dossier))
        create(Builder('task').within(dossier)
               .in_state('task-state-tested-and-closed'))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertFalse(dossier.is_open())
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has been succesfully resolved.'],
                          info_messages())


class TestResolving(FunctionalTestCase):

    def setUp(self):
        super(TestResolving, self).setUp()
        self.grant('Contributor', 'Editor', 'Reader', 'Reviewer')

    @browsing
    def test_set_end_date_to_earliest_possible_one(self, browser):
        dossier = create(Builder('dossier').having(start=date(2015, 1, 1)))
        subdossier = create(Builder('dossier')
                            .having(start=date(2015, 1, 1))
                            .within(dossier))
        with freeze(datetime(2016, 6, 1)):
            create(Builder('document').within(subdossier))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(date(2016, 6, 1), IDossier(dossier).end)
        self.assertEquals(date(2016, 6, 1), IDossier(subdossier).end,
                          'The end date has not been set recursively.')

    @browsing
    def test_resolves_the_dossier_and_subdossiers(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(subdossier))

    @browsing
    def test_lenient_resolver_skips_document_and_task_filing_check(self, browser):  # noqa
        api.portal.set_registry_record(
            'resolver_name', 'lenient', IDossierResolveProperties)

        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))
        create(Builder('document').within(dossier))
        create(Builder('mail').within(dossier))
        create(Builder('task')
               .within(dossier)
               .in_state('task-state-tested-and-closed'))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(subdossier))
        self.assertEquals(
            ['The dossier has been succesfully resolved.'], info_messages())

    @browsing
    def test_handles_already_resolved_subdossiers(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier')
                            .within(dossier)
                            .in_state('dossier-state-resolved'))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(subdossier))

    @browsing
    def test_inactive_subdossiers_stays_inactive(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier')
                            .within(dossier)
                            .in_state('dossier-state-inactive'))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-inactive',
                          api.content.get_state(subdossier))

    @browsing
    def test_resolving_only_a_subdossier_is_possible(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))

        browser.login().open(subdossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals('dossier-state-active',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(subdossier))
