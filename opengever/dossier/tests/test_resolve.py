from Acquisition import aq_parent
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
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.interfaces import IDossierResolveProperties
from opengever.testing import FunctionalTestCase
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


class TestResolverVocabulary(FunctionalTestCase):

    def test_resolver_vocabulary(self):
        vocabulary = get_resolver_vocabulary()
        self.assertItemsEqual(
            [u'strict', u'lenient'],
            vocabulary.by_value.keys())


class TestResolvingDossiers(FunctionalTestCase):

    @browsing
    def test_archive_form_is_omitted_for_sites_without_filing_number_support(self, browser):
        self.grant('Manager')
        dossier = create(Builder('dossier')
                         .having(start=date(2013, 11, 5)))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has been succesfully resolved.'],
                          info_messages())

    @browsing
    def test_archive_form_is_omitted_when_resolving_subdossiers(self, browser):
        self.grant('Manager')
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier')
                            .within(dossier)
                            .having(start=date(2013, 11, 5)))

        browser.login().open(subdossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(subdossier.absolute_url(), browser.url)
        self.assertEquals(['The subdossier has been succesfully resolved.'],
                          info_messages())


class TestResolveJobs(FunctionalTestCase):

    def setUp(self):
        super(TestResolveJobs, self).setUp()
        self.dossier = create(Builder('dossier').titled(u'Anfragen'))
        self.grant('Contributor', 'Editor', 'Reader', 'Reviewer')
        self.catalog = api.portal.get_tool('portal_catalog')

    def test_all_trashed_documents_are_deleted_when_resolving_a_dossier_if_enabled(self):
        api.portal.set_registry_record(
            'purge_trash_enabled', True, interface=IDossierResolveProperties)

        doc1 = create(Builder('document').within(self.dossier))
        doc2 = create(Builder('document').within(self.dossier).trashed())

        api.content.transition(obj=self.dossier,
                               transition='dossier-transition-resolve')

        docs = [brain.getObject() for brain in
                self.catalog.unrestrictedSearchResults(
                    path='/'.join(self.dossier.getPhysicalPath()))]

        self.assertIn(doc1, docs)
        self.assertNotIn(doc2, docs)

    def test_purge_trashs_recursive(self):
        api.portal.set_registry_record(
            'purge_trash_enabled', True, interface=IDossierResolveProperties)

        subdossier = create(Builder('dossier').within(self.dossier))
        doc1 = create(Builder('document').within(subdossier))
        doc2 = create(Builder('document').within(subdossier).trashed())

        api.content.transition(obj=self.dossier,
                               transition='dossier-transition-resolve')

        docs = [brain.getObject() for brain in
                self.catalog.unrestrictedSearchResults(
                    path='/'.join(self.dossier.getPhysicalPath()))]

        self.assertIn(doc1, docs)
        self.assertNotIn(doc2, docs)

    def test_purging_trashed_documents_is_disabled_by_default(self):
        api.portal.set_registry_record(
            'purge_trash_enabled', False, interface=IDossierResolveProperties)

        doc1 = create(Builder('document').within(self.dossier).trashed())
        api.content.transition(obj=self.dossier,
                               transition='dossier-transition-resolve')

        docs = [brain.getObject() for brain in
                self.catalog.unrestrictedSearchResults(
                    path='/'.join(self.dossier.getPhysicalPath()))]
        self.assertIn(doc1, docs)

    def test_adds_journal_pdf_when_enabled(self):
        api.portal.set_registry_record(
            'journal_pdf_enabled', True, interface=IDossierResolveProperties)

        with freeze(datetime(2016, 4, 25)):
            api.content.transition(obj=self.dossier,
                                   transition='dossier-transition-resolve')

        journal_pdf = self.dossier.get('document-1')
        self.assertEquals(u'Journal of dossier Anfragen, Apr 25, 2016 12:00 AM',
                          journal_pdf.title)
        self.assertEquals(u'journal-of-dossier-anfragen-apr-25-2016-12-00-am.pdf',
                          journal_pdf.file.filename)
        self.assertEquals(u'application/pdf',
                          journal_pdf.file.contentType)
        self.assertFalse(journal_pdf.preserved_as_paper)

    def test_journal_pdf_is_only_added_to_main_dossier(self):
        api.portal.set_registry_record(
            'journal_pdf_enabled', True, interface=IDossierResolveProperties)

        create(Builder('dossier').within(self.dossier))
        api.content.transition(obj=self.dossier,
                               transition='dossier-transition-resolve')

        docs = api.content.find(context=self.dossier,
                                depth=-1,
                                object_provides=[IBaseDocument])

        self.assertEquals(1, len(docs))
        self.assertEquals(self.dossier, aq_parent(docs[0].getObject()))

    def test_journal_pdf_is_disabled_by_default(self):
        doc1 = create(Builder('document').within(self.dossier))
        api.content.transition(obj=self.dossier,
                               transition='dossier-transition-resolve')

        self.assertEquals(
            [doc1], self.dossier.listFolderContents(),
            "Journal PDF created altough it's disabled by default.")

    def test_only_shadowed_documents_are_deleted_when_resolving_a_dossier(self):
        doc1 = create(Builder('document').within(self.dossier))
        doc2 = create(Builder('document').within(self.dossier).as_shadow_document())
        doc1.reindexObject(idxs=["review_state"])
        doc2.reindexObject(idxs=["review_state"])

        api.content.transition(obj=self.dossier,
                               transition='dossier-transition-resolve')

        docs = [brain.getObject() for brain in
                self.catalog.unrestrictedSearchResults(
                    path='/'.join(self.dossier.getPhysicalPath()))]

        self.assertIn(doc1, docs)
        self.assertNotIn(doc2, docs)

    def test_shadowed_documents_are_deleted_recursively_when_resolving_a_dossier(self):
        subdossier = create(Builder('dossier').within(self.dossier))
        doc1 = create(Builder('document').within(subdossier))
        doc2 = create(Builder('document').within(subdossier).as_shadow_document())
        doc1.reindexObject(idxs=["review_state"])
        doc2.reindexObject(idxs=["review_state"])

        api.content.transition(obj=self.dossier,
                               transition='dossier-transition-resolve')

        docs = [brain.getObject() for brain in
                self.catalog.unrestrictedSearchResults(
                    path='/'.join(self.dossier.getPhysicalPath()))]

        self.assertIn(doc1, docs)
        self.assertNotIn(doc2, docs)


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

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['not all task are closed'],
                          error_messages())

    @browsing
    def test_resolving_is_cancelled_when_dossier_has_an_invalid_end_date(self, browser):
        dossier = create(Builder('dossier').having(end=date(2016, 5, 7)))
        create(Builder('document')
               .within(dossier)
               .having(document_date=date(2016, 6, 1)))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals([],
                          error_messages())

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
        create(Builder('document')
               .within(subdossier)
               .having(document_date=date(2016, 6, 1)))

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
