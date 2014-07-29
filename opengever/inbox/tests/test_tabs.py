from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.testing import select_current_org_unit
from opengever.testing import task2sqltask


class TestInboxTabbedview(FunctionalTestCase):

    def setUp(self):
        super(TestInboxTabbedview, self).setUp()
        self.inbox = create(Builder('inbox').titled(u'Testinbox'))

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def test_trash_listing_does_not_contain_subdossier_and_checked_out_column(self):
        trash = self.inbox.restrictedTraverse('tabbedview_view-trash')

        columns = [col.get('column') for col in trash.columns if isinstance(col, dict)]
        self.assertNotIn('containing_subdossier', columns)
        self.assertNotIn('checked_out', columns)

    def test_trash_lists_only_documents_from_the_current_inbox(self):
        second_inbox = create(Builder('inbox'))

        create(Builder('document')
               .within(second_inbox)
               .titled('Doc 1')
               .trashed())

        document_2 = create(Builder('document')
                            .within(self.inbox)
                            .titled('Doc 2')
                            .trashed())

        view = self.inbox.restrictedTraverse('tabbedview_view-trash')
        view.update()

        self.assertEquals([document_2],
                          [brain.getObject() for brain in view.contents])


    def test_document_listings_does_not_contain_subdossier_and_checked_out_column(self):
        document_view = self.inbox.restrictedTraverse('tabbedview_view-documents')

        columns = [col.get('column') for col in document_view.columns
                   if isinstance(col, dict)]

        self.assertNotIn('containing_subdossier', columns)
        self.assertNotIn('checked_out', columns)

    def test_documents_listing_only_show_documents_from_the_current_inbox(self):
        second_inbox = create(Builder('inbox'))
        create(Builder('document')
               .within(second_inbox)
               .titled('Doc 1'))

        document_2 = create(Builder('document')
                            .within(self.inbox)
                            .titled('Doc 2'))

        view = self.inbox.restrictedTraverse('tabbedview_view-documents')
        view.update()

        self.assertEquals([document_2],
                          [brain.getObject() for brain in view.contents])


class TestInboxTaskTabs(FunctionalTestCase):

    viewname = ''

    def setUp(self):
        super(TestInboxTaskTabs, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.org_unit_2 = create(Builder('org_unit')
                                 .assign_users([self.user])
                                 .id('client2'))

        self.inbox = create(Builder('inbox').titled(u'Testinbox'))

    def assert_listing_results(self, results):
        view = self.inbox.restrictedTraverse(
            'tabbedview_view-{}'.format(self.viewname))
        view.update()

        self.assertEquals([task2sqltask(obj) for obj in results],
                          view.contents)


class TestAssignedInboxTaskTab(TestInboxTaskTabs):

    viewname = 'assigned_inbox_tasks'

    def test_lists_only_tasks_assigned_to_the_current_org_units_inbox(self):
        forwarding_1 = create(Builder('forwarding')
                              .within(self.inbox)
                              .having(responsible='inbox:client1'))
        forwarding_2 = create(Builder('forwarding')
                              .within(self.inbox)
                              .having(responsible='inbox:client2'))

        self.assert_listing_results([forwarding_1])

        select_current_org_unit('client2')
        self.assert_listing_results([forwarding_2])

    def test_list_tasks_and_forwardings(self):
        task = create(Builder('task')
                      .within(self.inbox)
                      .having(responsible='inbox:client1'))

        forwarding = create(Builder('forwarding')
                            .within(self.inbox)
                            .having(responsible='inbox:client1'))

        self.assert_listing_results([task, forwarding])


class TestIssuedInboxTaskTab(TestInboxTaskTabs):

    viewname = 'issued_inbox_tasks'

    def test_list_tasks_and_forwardings(self):
        task = create(Builder('task')
                      .within(self.inbox)
                      .having(issuer='inbox:client1'))

        forwarding = create(Builder('forwarding')
                            .within(self.inbox)
                            .having(issuer='inbox:client1'))

        self.assert_listing_results([task, forwarding])

    def test_list_only_task_with_current_org_units_inbox_as_a_issuer(self):
        task1 = create(Builder('task')
                      .within(self.inbox)
                      .having(issuer='inbox:client1'))

        task2 = create(Builder('task')
                      .within(self.inbox)
                      .having(issuer='inbox:client2'))

        self.assert_listing_results([task1])

        select_current_org_unit('client2')
        self.assert_listing_results([task2])

    def test_list_also_tasks_outside_of_the_inbox(self):
        task_inside = create(Builder('task')
              .within(self.inbox)
              .having(issuer='inbox:client1'))

        task_outside = create(Builder('task')
              .having(issuer='inbox:client1'))

        self.assert_listing_results([task_inside, task_outside])


class TestClosedForwardings(FunctionalTestCase):

    viewname = 'closed-forwardings'

    def setUp(self):
        super(TestClosedForwardings, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.yearfolder = create(Builder('yearfolder'))
        self.forwarding = create(Builder('forwarding')
                                 .within(self.yearfolder)
                                 .in_state('forwarding-state-closed'))

    def test_state_filter_is_deactivated(self):
        view = self.yearfolder.restrictedTraverse(
            'tabbedview_view-{}'.format(self.viewname))
        view.update()

        self.assertFalse(view.state_filter_available)
        self.assertEquals(
            [self.forwarding.get_sql_object()], view.contents)
