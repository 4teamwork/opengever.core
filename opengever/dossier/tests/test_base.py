from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID


class TestDossierContainerFunctional(FunctionalTestCase):
    """This test-case should eventually replace TestDossierContainer.
    New tests will be added to this case.
    """

    def setUp(self):
        super(TestDossierContainerFunctional, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

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


class TestDossierChecks(FunctionalTestCase):

    def setUp(self):
        super(TestDossierChecks, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def test_its_all_closed_if_no_task_exists(self):
        dossier = create(Builder("dossier"))
        self.assertTrue(dossier.is_all_closed())

    def test_its_all_closed_if_all_task_stays_in_an_inactive_state(self):
        dossier = create(Builder("dossier"))
        create(Builder("task").within(dossier)
               .in_state('task-state-cancelled'))
        create(Builder("task").within(dossier)
               .in_state('task-state-tested-and-closed'))
        create(Builder("task").within(dossier)
               .in_state('task-state-tested-and-closed'))

        self.assertTrue(dossier.is_all_closed())

    def test_its_all_closed_if_tasks_and_subtasks_stays_in_an_inactive_state(self):
        dossier = create(Builder("dossier"))
        task = create(Builder("task").within(dossier)
                      .in_state('task-state-cancelled'))
        subtask = create(Builder("task").within(task)
                         .in_state('task-state-cancelled'))
        create(Builder("task").within(subtask)
               .in_state('task-state-tested-and-closed'))

        self.assertTrue(dossier.is_all_closed())

    def test_its_not_all_closed_if_a_task_stays_in_an_active_state(self):
        dossier = create(Builder("dossier"))
        task = create(Builder("task").within(dossier)
                      .in_state('task-state-open'))

        self.assertFalse(dossier.is_all_closed())

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
               .checked_out_by(TEST_USER_ID))
        self.assertTrue(dossier.is_all_checked_in())

    def test_its_not_all_checked_in_when_a_document_inside_the_subdossier_is_checked_out(self):
        dossier = create(Builder("dossier"))
        subdossier = create(Builder("dossier").within(dossier))
        create(Builder('document')
               .within(subdossier)
               .checked_out_by(TEST_USER_ID))

        self.assertTrue(dossier.is_all_checked_in())


class TestDateCalculations(FunctionalTestCase):

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
        subdossier = create(Builder("dossier")
                            .within(dossier)
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
