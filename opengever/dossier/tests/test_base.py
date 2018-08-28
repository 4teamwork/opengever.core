from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from opengever.base.behaviors.changed import IChanged
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.testing import IntegrationTestCase
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import pytz


class TestDossierContainer(IntegrationTestCase):

    def test_is_all_supplied_without_any_subdossiers(self):
        self.login(self.dossier_responsible)
        create(Builder('document').within(self.empty_dossier))
        self.assertTrue(self.empty_dossier.is_all_supplied())

    def test_is_not_all_supplied_with_subdossier_and_document(self):
        self.login(self.dossier_responsible)
        create(Builder('dossier').within(self.empty_dossier))
        create(Builder('document').within(self.empty_dossier))
        self.assertFalse(self.empty_dossier.is_all_supplied())

    def test_is_not_all_supplied_with_subdossier_and_tasks(self):
        self.login(self.dossier_responsible)
        create(Builder('dossier').within(self.empty_dossier))
        create(Builder('task').within(self.empty_dossier)
               .having(responsible=self.regular_user.getId()))
        self.assertFalse(self.empty_dossier.is_all_supplied())

    def test_is_not_all_supplied_with_subdossier_and_mails(self):
        self.login(self.dossier_responsible)
        create(Builder('dossier').within(self.empty_dossier))
        create(Builder('mail').within(self.empty_dossier).with_dummy_message())
        self.assertFalse(self.empty_dossier.is_all_supplied())

    def test_is_all_supplied_with_subdossier_containing_tasks_or_documents(self):
        self.login(self.dossier_responsible)
        subdossier = create(Builder('dossier').within(self.empty_dossier))
        create(Builder('task').within(subdossier)
               .having(responsible=self.regular_user.getId()))
        create(Builder('document').within(subdossier))
        self.assertTrue(self.empty_dossier.is_all_supplied())

    def test_get_parents_dossier_returns_none_for_main_dossier(self):
        self.login(self.dossier_responsible)
        self.assertEquals(None, self.dossier.get_parent_dossier())

    def test_get_parents_dossier_returns_main_dossier_for_a_subdossier(self):
        self.login(self.dossier_responsible)
        self.assertEquals(self.dossier, self.subdossier.get_parent_dossier())

    def test_is_subdossier_is_false_for_main_dossiers(self):
        self.login(self.dossier_responsible)
        self.assertFalse(self.dossier.is_subdossier())

    def test_is_subdossier_is_true_for_dossiers_inside_a_dossier(self):
        self.login(self.dossier_responsible)
        self.assertTrue(self.subdossier.is_subdossier())

    def test_max_subdossier_depth_is_1_by_default(self):
        self.login(self.dossier_responsible)
        self.assertIn('opengever.dossier.businesscasedossier',
                      [fti.id for fti in self.dossier.allowedContentTypes()])

        self.assertNotIn('opengever.dossier.businesscasedossier',
                         [fti.id for fti in self.subdossier.allowedContentTypes()])

    def test_max_subdossier_depth_is_configurable(self):
        self.login(self.dossier_responsible)
        self.assertNotIn('opengever.dossier.businesscasedossier',
                         [fti.id for fti in self.subdossier.allowedContentTypes()])

        proxy = getUtility(IRegistry).forInterface(IDossierContainerTypes)
        proxy.maximum_dossier_depth = 2
        self.assertIn('opengever.dossier.businesscasedossier',
                      [fti.id for fti in self.subdossier.allowedContentTypes()])

    def test_get_subdossiers_is_recursive_by_default(self):
        self.login(self.dossier_responsible)
        self.assertSequenceEqual(
            [self.subdossier, self.subdossier2, self.subsubdossier],
            map(self.brain_to_object, self.dossier.get_subdossiers()))

        self.assertSequenceEqual(
            [self.subdossier, self.subdossier2],
            map(self.brain_to_object, self.dossier.get_subdossiers(depth=1)))

    def test_sequence_number(self):
        self.login(self.dossier_responsible)
        expected = {
            'dossier': 1,
            'subdossier': 2,
            'subdossier2': 3,
            'subsubdossier': 4,
            'expired_dossier': 5,
            'empty_dossier': 7}
        got = {name: getattr(self, name).get_sequence_number()
               for name in expected.keys()}
        self.assertDictEqual(expected, got)

    def test_support_participations(self):
        self.login(self.dossier_responsible)
        self.assertTrue(self.dossier.has_participation_support())

    def test_support_tasks(self):
        self.login(self.dossier_responsible)
        self.assertTrue(self.dossier.has_task_support())

    def test_reference_number(self):
        self.login(self.dossier_responsible)
        expected = {
            'dossier': 'Client1 1.1 / 1',
            'subdossier': 'Client1 1.1 / 1.1',
            'subdossier2': 'Client1 1.1 / 1.2',
            'expired_dossier': 'Client1 1.1 / 2',
            'empty_dossier': 'Client1 1.1 / 4'}
        got = {name: getattr(self, name).get_reference_number()
               for name in expected.keys()}
        self.assertDictEqual(expected, got)


class TestDossierChecks(IntegrationTestCase):

    def test_it_has_no_active_task_when_no_task_exists(self):
        self.login(self.dossier_responsible)
        self.assertFalse(self.empty_dossier.has_active_tasks())

    def test_has_active_tasks_false_when_states_cancelled(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-cancelled', *self.dossier_tasks)
        self.assertFalse(self.dossier.has_active_tasks())

    def test_has_active_tasks_false_when_states_tested_and_closed(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-tested-and-closed', *self.dossier_tasks)
        self.assertFalse(self.dossier.has_active_tasks())

    def test_has_active_tasks_true_when_states_in_progress(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-in-progress', *self.dossier_tasks)
        self.assertTrue(self.dossier.has_active_tasks())

    def test_has_active_tasks_true_when_states_open(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-open', *self.dossier_tasks)
        self.assertTrue(self.dossier.has_active_tasks())

    def test_has_active_tasks_true_when_states_rejected(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-rejected', *self.dossier_tasks)
        self.assertTrue(self.dossier.has_active_tasks())

    def test_has_active_tasks_true_when_states_resolved(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-resolved', *self.dossier_tasks)
        self.assertTrue(self.dossier.has_active_tasks())

    def test_has_active_tasks_checks_are_recursive(self):
        self.login(self.dossier_responsible)
        first, second = self.dossier_tasks[:2]
        self.set_workflow_state('task-state-resolved', first)
        self.set_workflow_state('task-state-tested-and-closed', second)
        self.assertTrue(self.dossier.has_active_tasks())

        self.set_workflow_state('task-state-resolved', second)
        self.set_workflow_state('task-state-tested-and-closed', first)
        self.assertTrue(self.dossier.has_active_tasks())

    def test_is_all_checked_in_is_true_when_no_document_exists(self):
        self.login(self.dossier_responsible)
        self.assertTrue(self.empty_dossier.is_all_checked_in())

    def test_is_all_checked_in_is_true_when_no_document_is_checked_out(self):
        self.login(self.dossier_responsible)
        self.assertTrue(self.dossier.is_all_checked_in())

    def test_is_all_checked_in_is_false_when_document_in_dossier_checked_out(self):
        self.login(self.dossier_responsible)
        self.assertTrue(self.dossier.is_all_checked_in())
        self.checkout_document(self.document)
        self.assertFalse(self.dossier.is_all_checked_in())

    def test_is_all_checked_in_is_false_when_document_in_subdossier_checked_out(self):
        self.login(self.dossier_responsible)
        self.assertTrue(self.dossier.is_all_checked_in())
        self.checkout_document(self.document)
        self.assertFalse(self.dossier.is_all_checked_in())


class TestDateCalculations(IntegrationTestCase):

    @browsing
    def test_start_date_defaults_to_today(self, browser):
        self.login(self.regular_user, browser)
        with freeze(datetime(2015, 12, 22)):
            browser.open(self.leaf_repofolder)
            factoriesmenu.add('Business Case Dossier')
            self.assertEquals('22.12.2015', browser.find('Opening Date').value)

    def test_earliest_possible_is_none_for_empty_dossiers(self):
        self.login(self.dossier_responsible)
        IDossier(self.empty_dossier).start = None
        IDossier(self.empty_dossier).end = None
        self.empty_dossier.reindexObject(idxs=['end', 'start'])
        self.assertIsNone(self.empty_dossier.earliest_possible_end_date())

    def test_earliest_possible_is_end_date_of_a_dossiers(self):
        self.login(self.dossier_responsible)
        IDossier(self.empty_dossier).start = None
        IDossier(self.empty_dossier).end = date(2029, 9, 18)
        self.empty_dossier.reindexObject(idxs=['end', 'start'])
        self.assertEquals(date(2029, 9, 18),
                          self.empty_dossier.earliest_possible_end_date())

    def test_earliest_possible_is_last_modified_document_modification_date(self):
        self.login(self.dossier_responsible)
        IChanged(self.document).changed = datetime(2021, 1, 22, tzinfo=pytz.utc)
        self.document.reindexObject(idxs=['changed'])
        self.assertEquals(date(2021, 1, 22),
                          self.dossier.earliest_possible_end_date())

    def test_earliest_possible_is_latest_of_dossiers_end_dates_and_document_modificiation_dates(self):
        self.login(self.dossier_responsible)

        IChanged(self.document).changed = datetime(2020, 1, 1, tzinfo=pytz.utc)
        self.document.reindexObject(idxs=['changed'])
        IDossier(self.subdossier).end = date(2020, 2, 2)
        self.subdossier.reindexObject(idxs=['end'])
        self.assertEquals(date(2020, 2, 2), self.dossier.earliest_possible_end_date())

        IChanged(self.document).changed = datetime(2020, 3, 3, tzinfo=pytz.utc)
        self.document.reindexObject(idxs=['changed'])
        self.assertEquals(date(2020, 3, 3), self.dossier.earliest_possible_end_date())

    def test_calculation_ignore_inactive_subdossiers_for_calculation(self):
        self.login(self.dossier_responsible)

        IDossier(self.subdossier).end = date(2020, 1, 1)
        self.subdossier.reindexObject(idxs=['end'])
        IDossier(self.subdossier2).end = date(2020, 2, 2)
        self.subdossier2.reindexObject(idxs=['end'])
        self.assertEquals(date(2020, 2, 2), self.dossier.earliest_possible_end_date())

        self.set_workflow_state('dossier-state-inactive', self.subdossier2)
        self.assertEquals(date(2020, 1, 1), self.dossier.earliest_possible_end_date())

    def test_none_is_not_a_valid_start_date(self):
        self.login(self.dossier_responsible)
        IDossier(self.empty_dossier).start = None
        IDossier(self.empty_dossier).end = None
        self.empty_dossier.reindexObject(idxs=['end', 'start'])
        self.assertIsNone(self.empty_dossier.earliest_possible_end_date())
        self.assertFalse(self.empty_dossier.has_valid_startdate())

    def test_every_date_is_a_valid_start_date(self):
        self.login(self.dossier_responsible)
        self.assertEquals(date(2016, 1, 1),
                          self.empty_dossier.earliest_possible_end_date())
        self.assertTrue(self.empty_dossier.has_valid_startdate())

    def test_no_end_date_is_valid(self):
        self.login(self.dossier_responsible)
        self.assertIsNone(IDossier(self.empty_dossier).end)
        self.assertTrue(self.empty_dossier.has_valid_enddate())

    def test_dossier_end_can_be_later_than_document_date(self):
        self.login(self.dossier_responsible)
        IDossier(self.dossier).end = date(2020, 2, 2)
        IChanged(self.document).changed = datetime(2020, 1, 1, tzinfo=pytz.utc)
        self.document.reindexObject(idxs=['changed'])
        self.assertTrue(self.dossier.has_valid_enddate())

    def test_dossier_end_can_be_equal_to_document_modification_date(self):
        self.login(self.dossier_responsible)
        IDossier(self.dossier).end = date(2020, 1, 1)
        IChanged(self.document).changed = datetime(2020, 1, 1, tzinfo=pytz.utc)
        self.document.reindexObject(idxs=['changed'])
        self.assertTrue(self.dossier.has_valid_enddate())

    def test_dossier_end_cannot_be_earlier_to_document_date(self):
        self.login(self.dossier_responsible)
        IDossier(self.dossier).end = date(2020, 1, 1)
        IChanged(self.document).changed = datetime(2020, 2, 2, tzinfo=pytz.utc)
        self.document.reindexObject(idxs=['changed'])
        self.assertFalse(self.dossier.has_valid_enddate())

    def test_end_date_is_allways_valid_in_a_empty_dossier(self):
        self.login(self.dossier_responsible)
        IDossier(self.empty_dossier).end = date(2050, 1, 1)
        self.assertTrue(self.empty_dossier.has_valid_enddate())

        IDossier(self.empty_dossier).end = None
        self.assertTrue(self.empty_dossier.has_valid_enddate())

    def test_get_former_state_returns_last_end_state_in_history(self):
        self.login(self.administrator)
        dossier = self.empty_dossier
        api.content.transition(obj=dossier, transition='dossier-transition-deactivate')
        self.assertEquals('dossier-state-inactive', dossier.get_former_state())
        api.content.transition(obj=dossier, transition='dossier-transition-activate')
        self.assertEquals('dossier-state-inactive', dossier.get_former_state())
        api.content.transition(obj=dossier, transition='dossier-transition-resolve')
        self.assertEquals('dossier-state-resolved', dossier.get_former_state())
        api.content.transition(obj=dossier, transition='dossier-transition-reactivate')
        self.assertEquals('dossier-state-resolved', dossier.get_former_state())

    def test_get_former_state_returns_none_for_dossiers_was_never_in_an_end_state(self):
        self.login(self.dossier_responsible)
        self.assertIsNone(self.dossier.get_former_state())

    def test_earliest_possible_can_handle_datetime_objs(self):
        self.login(self.dossier_responsible)

        IChanged(self.document).changed = datetime(2020, 1, 1, 10, 10, tzinfo=pytz.utc)
        self.document.reindexObject(idxs=['changed'])
        IDossier(self.subdossier).end = datetime(2020, 2, 2, 10, 10)
        self.subdossier.reindexObject(idxs=['end'])
        self.assertEquals(date(2020, 2, 2), self.dossier.earliest_possible_end_date())

    def test_is_addable(self):
        self.login(self.dossier_responsible)
        self.assertTrue(self.dossier.is_addable('opengever.document.document'))
        self.assertFalse(self.expired_dossier.is_addable('opengever.document.document'))
