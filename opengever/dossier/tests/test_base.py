from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.testing import FunctionalTestCase
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestDossierContainer(FunctionalTestCase):

    def setUp(self):
        super(TestDossierContainer, self).setUp()

    def test_is_all_supplied_without_any_subdossiers(self):
        dossier = create(Builder("dossier"))
        create(Builder("document").within(dossier))

        self.assertTrue(dossier.is_all_supplied())

    def test_is_not_all_supplied_with_subdossier_and_document(self):
        dossier = create(Builder("dossier"))
        create(Builder("dossier").within(dossier))
        create(Builder("document").within(dossier))

        self.assertFalse(dossier.is_all_supplied())

    def test_is_not_all_supplied_with_subdossier_and_tasks(self):
        dossier = create(Builder("dossier"))
        create(Builder("dossier").within(dossier))
        create(Builder("task").within(dossier))

        self.assertFalse(dossier.is_all_supplied())

    def test_is_not_all_supplied_with_subdossier_and_mails(self):
        dossier = create(Builder("dossier"))
        create(Builder("dossier").within(dossier))
        create(Builder("mail").within(dossier)
               .with_dummy_message())

        self.assertFalse(dossier.is_all_supplied())

    def test_is_all_supplied_with_subdossier_containing_tasks_or_documents(self):
        dossier = create(Builder("dossier"))
        subdossier = create(Builder("dossier").within(dossier))
        create(Builder("task").within(subdossier))
        create(Builder("document").within(subdossier))

        self.assertTrue(dossier.is_all_supplied())

    def test_get_parents_dossier_returns_none_for_main_dossier(self):
        dossier = create(Builder('dossier'))
        self.assertEquals(None, dossier.get_parent_dossier())

    def test_get_parents_dossier_returns_main_dossier_for_a_subdossier(self):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))
        self.assertEquals(dossier, subdossier.get_parent_dossier())

    def test_is_subdossier_is_false_for_main_dossiers(self):
        dossier = create(Builder('dossier'))
        self.assertFalse(dossier.is_subdossier())

    def test_is_subdossier_is_true_for_dossiers_inside_a_dossier(self):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))
        self.assertTrue(subdossier.is_subdossier())

    def test_maximum_dossier_level_is_2_by_default(self):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))

        self.assertIn('opengever.dossier.businesscasedossier',
                      [fti.id for fti in dossier.allowedContentTypes()])

        self.assertNotIn('opengever.dossier.businesscasedossier',
                         [fti.id for fti in subdossier.allowedContentTypes()])

    def test_get_subdossier_depth_from_registry(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IDossierContainerTypes)
        proxy.maximum_dossier_depth = 2

        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))
        subsubdossier = create(Builder('dossier').within(subdossier))

        self.assertNotIn(
            'opengever.dossier.businesscasedossier',
            [fti.id for fti in subsubdossier.allowedContentTypes()])

    def test_get_subdossiers_returns_subsubdossiers_as_well(self):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))
        subsubdossier = create(Builder('dossier').within(subdossier))

        self.assertSequenceEqual(
            [subdossier, subsubdossier],
            self.brains_to_objects(dossier.get_subdossiers()))

    def test_get_subdossiers_depth(self):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))
        create(Builder('dossier').within(subdossier))

        self.assertSequenceEqual(
            [subdossier],
            self.brains_to_objects(dossier.get_subdossiers(depth=1)))

    def test_sequence_number(self):
        dossier_1 = create(Builder("dossier"))
        subdossier = create(Builder("dossier"))
        dossier_2 = create(Builder("dossier"))

        self.assertEquals(1, dossier_1.get_sequence_number())
        self.assertEquals(2, subdossier.get_sequence_number())
        self.assertEquals(3, dossier_2.get_sequence_number())

    def test_support_participations(self):
        dossier = create(Builder("dossier"))
        self.assertTrue(dossier.has_participation_support())

    def test_support_tasks(self):
        dossier = create(Builder("dossier"))
        self.assertTrue(dossier.has_task_support())

    def test_reference_number(self):
        root = create(Builder('repository_root'))
        repo = create(Builder('repository').within(root))
        dossier_1 = create(Builder("dossier").within(repo))
        subdossier = create(Builder("dossier").within(dossier_1))
        dossier_2 = create(Builder("dossier").within(repo))

        self.assertEquals('Client1 1 / 1', dossier_1.get_reference_number())
        self.assertEquals('Client1 1 / 1.1', subdossier.get_reference_number())
        self.assertEquals('Client1 1 / 2', dossier_2.get_reference_number())


class TestDossierChecks(FunctionalTestCase):

    def test_it_has_no_active_task_when_no_task_exists(self):
        dossier = create(Builder("dossier"))
        self.assertFalse(dossier.has_active_tasks())

    def test_it_has_no_active_task_if_all_task_are_in_an_inactive_state(self):
        dossier = create(Builder("dossier"))
        create(Builder("task").within(dossier)
               .in_state('task-state-cancelled'))
        create(Builder("task").within(dossier)
               .in_state('task-state-tested-and-closed'))
        create(Builder("task").within(dossier)
               .in_state('task-state-tested-and-closed'))

        self.assertFalse(dossier.has_active_tasks())

    def test_it_has_no_active_task_if_tasks_and_subtasks_are_in_an_inactive_state(self):
        dossier = create(Builder("dossier"))
        task = create(Builder("task").within(dossier)
                      .in_state('task-state-cancelled'))
        subtask = create(Builder("task").within(task)
                         .in_state('task-state-cancelled'))
        create(Builder("task").within(subtask)
               .in_state('task-state-tested-and-closed'))

        self.assertFalse(dossier.has_active_tasks())

    def test_it_has_active_tasks_if_a_task_is_in_an_active_state(self):
        dossier = create(Builder("dossier"))
        create(Builder("task").within(dossier)
               .in_state('task-state-open'))

        self.assertTrue(dossier.has_active_tasks())

    def test_has_active_tasks_checks_recursive(self):
        dossier = create(Builder("dossier"))
        subdossier = create(Builder("dossier").within(dossier))
        subsubdossier = create(Builder("dossier").within(subdossier))
        create(Builder("task").within(subsubdossier).in_state('task-state-open'))

        self.assertTrue(dossier.has_active_tasks())

    def test_its_all_checked_in_when_no_document_exists(self):
        dossier = create(Builder("dossier"))
        self.assertTrue(dossier.is_all_checked_in())

    def test_its_all_checked_in_when_no_document_is_checked_out(self):
        dossier = create(Builder("dossier"))
        create(Builder('document').within(dossier))
        self.assertTrue(dossier.is_all_checked_in())

    def test_its_not_all_checked_in_when_a_document_inside_the_dossier_is_checked_out(self):
        dossier = create(Builder("dossier"))
        create(Builder('document')
               .within(dossier)
               .checked_out())
        self.assertFalse(dossier.is_all_checked_in())

    def test_its_not_all_checked_in_when_a_document_inside_the_subdossier_is_checked_out(self):
        dossier = create(Builder("dossier"))
        subdossier = create(Builder("dossier").within(dossier))
        create(Builder('document')
               .within(subdossier)
               .checked_out())

        self.assertFalse(dossier.is_all_checked_in())


class TestDateCalculations(FunctionalTestCase):

    def test_start_date_defaults_to_today(self):
        with freeze(datetime.now()):
            dossier = create(Builder("dossier"))
            self.assertEqual(IDossier(dossier).start, date.today())

    def test_earliest_possible_is_none_for_empty_dossiers(self):
        dossier = create(Builder("dossier")
                         .having(start=None))
        self.assertEquals(None, dossier.earliest_possible_end_date())

    def test_earliest_possible_is_end_date_of_a_dossiers(self):
        dossier = create(Builder("dossier")
                         .having(start=date(2012, 01, 01),
                                 end=date(2012, 02, 03)))
        self.assertEquals(date(2012, 02, 03),
                          dossier.earliest_possible_end_date())

    def test_earliest_possible_is_latest_document_date(self):
        dossier = create(Builder("dossier").having(start=date(2012, 01, 01)))
        create(Builder("document").within(dossier)
               .having(document_date=date(2012, 02, 03)))
        create(Builder("document").within(dossier)
               .having(document_date=date(2012, 01, 01)))

        self.assertEquals(date(2012, 02, 03),
                          dossier.earliest_possible_end_date())

    def test_earliest_possible_is_latest_of_dossiers_end_dates_and_document_dates(self):
        dossier = create(Builder("dossier")
                         .having(start=date(2012, 01, 01),
                                 end=date(2012, 02, 04)))
        create(Builder("dossier").within(dossier)
               .having(start=date(2012, 01, 01),
                       end=date(2012, 02, 03)))
        create(Builder("document").within(dossier)
               .having(document_date=date(2012, 02, 05)))

        self.assertEquals(date(2012, 02, 05),
                          dossier.earliest_possible_end_date())

    def test_calculation_ignore_inactive_subdossiers_for_calculation(self):
        dossier = create(Builder("dossier")
                         .having(start=date(2012, 01, 01),
                                 end=date(2012, 02, 04)))

        create(Builder("dossier").within(dossier)
               .having(start=date(2012, 01, 01), end=date(2012, 02, 05))
               .in_state('dossier-state-inactive'))

        self.assertEquals(date(2012, 02, 04),
                          dossier.earliest_possible_end_date())

    def test_none_is_not_a_valid_start_date(self):
        dossier = create(Builder("dossier").having(start=None))

        self.assertFalse(dossier.has_valid_startdate(),
                         "None is not a valid dossier startdate")

    def test_every_date_is_a_valid_start_date(self):
        dossier = create(Builder("dossier")
                         .having(start=date(2012, 02, 24)))

        self.assertTrue(
            dossier.has_valid_startdate(),
            "'%s' should be a valid startdate" % IDossier(dossier).start)

    def test_no_end_date_is_valid(self):
        dossier = create(Builder("dossier"))
        create(Builder("dossier").within(dossier)
               .having(start=date(2012, 02, 24)))
        self.assertTrue(dossier.has_valid_enddate())

    def test_end_date_afterward_the_latest_document_date_is_valid(self):
        dossier = create(Builder("dossier")
                         .having(start=date(2012, 01, 01),
                                 end=date(2012, 01, 02)))
        create(Builder('document')
               .within(dossier)
               .having(document_date=date(2012, 01, 01)))

        self.assertTrue(dossier.has_valid_enddate())

    def test_end_date_equal_the_latest_document_date_is_valid(self):
        dossier = create(Builder("dossier")
                         .having(start=date(2012, 01, 01),
                                 end=date(2012, 01, 01)))
        create(Builder('document')
               .within(dossier)
               .having(document_date=date(2012, 01, 01)))

        self.assertTrue(dossier.has_valid_enddate())

    def test_end_date_before_the_latest_document_date_is_invalid(self):
        dossier = create(Builder("dossier")
                         .having(start=date(2012, 01, 01),
                                 end=date(2012, 01, 01)))

        create(Builder('document')
               .within(dossier)
               .having(document_date=date(2012, 01, 02)))

        self.assertFalse(dossier.has_valid_enddate())

    def test_end_date_is_allways_valid_in_a_empty_dossier(self):
        dossier = create(Builder("dossier").having(
            start=date(2012, 01, 01),
            end=date(2012, 01, 01)))

        self.assertTrue(dossier.has_valid_enddate())

    def test_get_former_state_returns_last_end_state_in_history(self):
        self.grant('Manager', 'Editor', 'Publisher', 'Reviewer')

        dossier = create(Builder("dossier"))

        api.content.transition(obj=dossier, transition='dossier-transition-deactivate')
        api.content.transition(obj=dossier, transition='dossier-transition-activate')
        api.content.transition(obj=dossier, transition='dossier-transition-resolve')
        api.content.transition(obj=dossier, transition='dossier-transition-offer')
        api.content.transition(obj=dossier, transition='dossier-transition-archive')

        self.assertEquals('dossier-state-resolved', dossier.get_former_state())

    def test_get_former_state_returns_none_for_dossiers_was_never_in_an_end_state(self):
        self.grant('Manager', 'Editor', 'Publisher', 'Reviewer')

        dossier = create(Builder("dossier"))
        self.assertIsNone(dossier.get_former_state())
