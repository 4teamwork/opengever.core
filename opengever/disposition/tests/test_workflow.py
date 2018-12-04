from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.security import elevated_privileges
from opengever.disposition.interfaces import IAppraisal
from opengever.testing import IntegrationTestCase
from plone import api
from plone.api.exc import InvalidParameterError


class TestDispositionWorkflowIntegration(IntegrationTestCase):

    def test_initial_state_is_in_progress(self):
        self.login(self.records_manager)
        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(self.disposition))

    def test_dispositon_in_progress_can_be_refused_by_an_archivist(self):
        self.login(self.archivist)
        api.content.transition(self.disposition, 'disposition-transition-refuse')
        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(self.disposition))

    def test_dispositon_in_disposed_state_can_be_refused_by_an_archivist(self):

        with elevated_privileges():
            api.content.transition(self.disposition, to_state='disposition-state-disposed')

        self.login(self.archivist)
        api.content.transition(self.disposition, 'disposition-transition-refuse')
        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(self.disposition))

    def test_archivist_is_not_allowed_to_dispose_a_disposition(self):
        self.login(self.archivist)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        with self.assertRaises(InvalidParameterError):
            api.content.transition(self.disposition,
                                   'disposition-transition-dispose')

        self.login(self.records_manager)
        api.content.transition(self.disposition, 'disposition-transition-dispose')

    def test_dispose_is_only_allowed_when_disposition_contains_dossier_to_archive(self):
        self.login(self.archivist)
        appraisal = IAppraisal(self.disposition)
        appraisal.update(dossier=self.offered_dossier_to_archive, archive=False)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        self.login(self.records_manager)
        with self.assertRaises(InvalidParameterError):
            api.content.transition(self.disposition,
                                   'disposition-transition-dispose')

        appraisal.update(dossier=self.offered_dossier_to_archive, archive=True)
        api.content.transition(self.disposition, 'disposition-transition-dispose')

    def test_direct_close_is_not_allowed_when_disposition_contains_dossier_to_archive(self):
        self.login(self.archivist)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        appraisal = IAppraisal(self.disposition)
        self.assertTrue(appraisal.get(self.offered_dossier_to_archive))

        self.login(self.records_manager)
        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-appraised-to-closed')

        appraisal.update(dossier=self.offered_dossier_to_archive, archive=False)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraised-to-closed')

    def test_direct_close_is_not_allowed_for_archivists(self):
        self.login(self.archivist)
        appraisal = IAppraisal(self.disposition)
        appraisal.update(dossier=self.offered_dossier_to_archive, archive=False)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-appraised-to-closed')

        self.login(self.records_manager)
        api.content.transition(self.disposition,
                               'disposition-transition-appraised-to-closed')

    def test_records_manager_is_not_allowed_to_archive_a_disposition(self):
        self.login(self.records_manager)
        with self.login(self.archivist):
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-appraise')

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-dispose')

        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-archive')

        self.login(self.archivist)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-archive')

    def test_archivist_is_not_allowed_to_close_a_disposition(self):
        with elevated_privileges():
            api.content.transition(obj=self.disposition,
                                   to_state='disposition-state-archived')

        self.login(self.archivist)
        with self.assertRaises(InvalidParameterError):
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-close')

        self.login(self.records_manager)
        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-close')

    def test_when_appraising_final_archival_value_is_stored_on_dossier(self):
        self.login(self.archivist)

        appraisal = IAppraisal(self.disposition)
        self.assertEquals(
            ARCHIVAL_VALUE_WORTHY,
            ILifeCycle(self.offered_dossier_to_archive).archival_value)
        self.assertEquals(
            ARCHIVAL_VALUE_UNWORTHY,
            ILifeCycle(self.offered_dossier_to_destroy).archival_value)

        appraisal.update(dossier=self.offered_dossier_to_archive, archive=False)
        appraisal.update(dossier=self.offered_dossier_to_destroy, archive=True)
        api.content.transition(
            self.disposition, transition='disposition-transition-appraise')

        self.assertEquals(
            ARCHIVAL_VALUE_UNWORTHY,
            ILifeCycle(self.offered_dossier_to_archive).archival_value)
        self.assertEquals(
            ARCHIVAL_VALUE_WORTHY,
            ILifeCycle(self.offered_dossier_to_destroy).archival_value)

    @browsing
    def test_appraising_is_not_possible_if_the_appraisal_is_incomplete(self, browser):
        self.login(self.archivist, browser)
        appraisal = IAppraisal(self.disposition)
        appraisal.update(dossier=self.offered_dossier_to_archive, archive=None)

        browser.open(self.disposition)
        browser.click_on('disposition-transition-appraise')

        self.assertEquals(
            ['The appraisal is incomplete, appraisal could not be finalized.'],
            error_messages())
        self.assertEquals('disposition-state-in-progress',
                          api.content.get_state(self.disposition))

        appraisal.update(dossier=self.offered_dossier_to_archive, archive=True)

        browser.open(self.disposition)
        browser.click_on('disposition-transition-appraise')
        self.assertEquals('disposition-state-appraised',
                          api.content.get_state(self.disposition))

    def test_set_all_dossiers_to_archived_state_when_archiving_disposition(self):
        self.login(self.archivist)
        self.assertEquals('dossier-state-offered',
                          api.content.get_state(self.offered_dossier_to_archive))
        self.assertEquals('dossier-state-offered',
                          api.content.get_state(self.offered_dossier_to_destroy))

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-appraise')

        with self.login(self.records_manager):
            api.content.transition(obj=self.disposition,
                                   transition='disposition-transition-dispose')

        api.content.transition(obj=self.disposition,
                               transition='disposition-transition-archive')

        self.assertEquals('dossier-state-archived',
                          api.content.get_state(self.offered_dossier_to_archive))
        self.assertEquals('dossier-state-archived',
                          api.content.get_state(self.offered_dossier_to_destroy))

    @browsing
    def test_transfer_number_is_only_editable_by_archivist(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, view='edit')

        with self.assertRaises(FormFieldNotFound):
            browser.fill({'Transfer number': 'AB 123'})
        browser.css("#form-buttons-cancel").first.click()

        self.login(self.archivist, browser)
        browser.open(self.disposition, view='edit')

        browser.fill({'Transfer number': 'AB 123'})
        browser.click_on('Save')

        self.assertEquals('AB 123', self.disposition.transfer_number)
