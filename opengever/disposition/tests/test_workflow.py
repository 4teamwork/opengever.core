from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_PROMPT
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_SAMPLING
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition.interfaces import IAppraisal
from opengever.testing import FunctionalTestCase
from plone import api
from plone.api.exc import InvalidParameterError
import transaction


class TestDispositionWorkflow(FunctionalTestCase):

    def setUp(self):
        super(TestDispositionWorkflow, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_PROMPT)
                               .within(self.repository))
        self.dossier2 = create(Builder('dossier')
                               .as_expired()
                               .having(archival_value=ARCHIVAL_VALUE_SAMPLING)
                               .within(self.repository))

        self.grant('Records Manager')
        self.disposition = create(Builder('disposition')
                                  .having(dossiers=[self.dossier1, self.dossier2])
                                  .within(self.root))

    def test_initial_state_is_in_progress(self):
        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(self.disposition))

    def test_dispositon_in_progress_can_be_refused_by_an_archivist(self):
        self.grant('Archivist')
        api.content.transition(self.disposition, 'disposition-transition-refuse')
        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(self.disposition))

    def test_dispositon_in_disposed_state_can_be_refused_by_an_archivist(self):
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-disposed'))

        self.grant('Archivist')
        api.content.transition(disposition, 'disposition-transition-refuse')
        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(disposition))

    def test_archivist_is_not_allowed_to_dispose_a_disposition(self):
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-appraised'))
        IAppraisal(disposition).update(dossier=self.dossier1, archive=True)
        IAppraisal(disposition).update(dossier=self.dossier2, archive=True)

        with self.assertRaises(InvalidParameterError):
            self.grant('Archivist')
            api.content.transition(disposition,
                                   'disposition-transition-dispose')

        self.grant('Records Manager')
        api.content.transition(disposition, 'disposition-transition-dispose')

    def test_dispose_is_only_allowed_when_disposition_contains_dossier_to_archive(self):
        self.grant('Archivist')
        appraisal = IAppraisal(self.disposition)
        appraisal.update(dossier=self.dossier1, archive=False)
        appraisal.update(dossier=self.dossier2, archive=False)
        api.content.transition(self.disposition,
                               'disposition-transition-appraise')

        self.grant('Records Manager')
        with self.assertRaises(InvalidParameterError):
            api.content.transition(self.disposition,
                                   'disposition-transition-dispose')

        appraisal.update(dossier=self.dossier1, archive=True)
        api.content.transition(self.disposition, 'disposition-transition-dispose')

    def test_direct_close_is_not_allowed_when_disposition_contains_dossier_to_archive(self):
        self.grant('Archivist')
        appraisal = IAppraisal(self.disposition)
        appraisal.update(dossier=self.dossier1, archive=True)
        appraisal.update(dossier=self.dossier2, archive=False)
        api.content.transition(self.disposition,
                               'disposition-transition-appraise')

        self.grant('Records Manager')
        with self.assertRaises(InvalidParameterError):
            api.content.transition(self.disposition,
                                   'disposition-transition-appraised-to-closed')

        appraisal.update(dossier=self.dossier1, archive=False)
        api.content.transition(self.disposition,
                               'disposition-transition-appraised-to-closed')

    def test_direct_close_is_not_allowed_for_archivists(self):
        self.grant('Archivist')
        appraisal = IAppraisal(self.disposition)
        appraisal.update(dossier=self.dossier1, archive=False)
        appraisal.update(dossier=self.dossier2, archive=False)
        api.content.transition(self.disposition,
                               'disposition-transition-appraise')

        with self.assertRaises(InvalidParameterError):
            api.content.transition(self.disposition,
                                   'disposition-transition-appraised-to-closed')

        self.grant('Records Manager')
        api.content.transition(self.disposition,
                               'disposition-transition-appraised-to-closed')

    def test_records_manager_is_not_allowed_to_archive_a_disposition(self):
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-disposed'))

        with self.assertRaises(InvalidParameterError):
            self.grant('Records Manager')
            api.content.transition(disposition,
                                   'disposition-transition-archive')

        self.grant('Archivist')
        api.content.transition(disposition, 'disposition-transition-archive')

    def test_archivist_is_not_allowed_to_close_a_disposition(self):
        disposition = create(Builder('disposition')
                             .in_state('disposition-state-archived'))

        with self.assertRaises(InvalidParameterError):
            self.grant('Archivist')
            api.content.transition(disposition,
                                   'disposition-transition-close')

        self.grant('Records Manager')
        api.content.transition(disposition, 'disposition-transition-close')

    def test_when_appraising_final_archival_value_is_stored_on_dossier(self):
        self.grant('Archivist')

        IAppraisal(self.disposition).update(
            dossier=self.dossier1, archive=False)
        IAppraisal(self.disposition).update(
            dossier=self.dossier2, archive=True)

        api.content.transition(
            self.disposition, transition='disposition-transition-appraise')

        self.assertEquals(
            ARCHIVAL_VALUE_UNWORTHY, ILifeCycle(self.dossier1).archival_value)
        self.assertEquals(
            ARCHIVAL_VALUE_WORTHY, ILifeCycle(self.dossier2).archival_value)

    @browsing
    def test_appraising_is_not_possible_if_the_appraisal_is_incomplete(self, browser):
        self.grant('Archivist')
        browser.login().open(self.disposition)
        browser.click_on('disposition-transition-appraise')

        self.assertEquals(
            ['The appraisal is incomplete, appraisal could not be finalized.'],
            error_messages())
        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(self.disposition))

        appraisal = IAppraisal(self.disposition)
        appraisal.update(dossier=self.dossier1, archive=False)
        appraisal.update(dossier=self.dossier2, archive=True)
        transaction.commit()

        browser.login().open(self.disposition)
        browser.click_on('disposition-transition-appraise')
        self.assertEquals('disposition-state-appraised',
                          api.content.get_state(self.disposition))

    def test_when_archiving_all_dossiers_moved_to_archived_set_to_archive_state(self):
        self.grant('Archivist', 'Records Manager')
        IAppraisal(self.disposition).update(dossier=self.dossier1, archive=True)
        IAppraisal(self.disposition).update(dossier=self.dossier2, archive=True)
        api.content.transition(
            self.disposition, transition='disposition-transition-appraise')
        api.content.transition(
            self.disposition, transition='disposition-transition-dispose')

        api.content.transition(
            self.disposition, transition='disposition-transition-archive')

        self.assertEquals(
            'dossier-state-archived', api.content.get_state(self.dossier1))
        self.assertEquals(
            'dossier-state-archived', api.content.get_state(self.dossier2))

    @browsing
    def test_transfer_number_is_only_editable_by_archivist(self, browser):
        self.grant('Records Manager')
        browser.login().open(self.disposition, view='edit')

        with self.assertRaises(FormFieldNotFound):
            browser.fill({'Transfer number': 'AB 123'})
            browser.click_on('Save')

        self.grant('Archivist')
        browser.login().open(self.disposition, view='edit')
        browser.fill({'Transfer number': 'AB 123'})
        browser.click_on('Save')

        self.assertEquals('AB 123', self.disposition.transfer_number)
