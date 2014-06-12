from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import create_client
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing import task2sqltask


class TestInboxTabs(FunctionalTestCase):

    def setUp(self):
        super(TestInboxTabs, self).setUp()
        self.inbox = create(Builder('inbox').titled(u'Testinbox'))

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def test_trash_listing_does_not_contain_subdossier_and_checked_out_column(self):
        trash = self.inbox.restrictedTraverse('tabbedview_view-trash')

        columns = [col.get('column') for col in trash.columns if isinstance(col, dict)]
        self.assertNotIn('containing_subdossier', columns)
        self.assertNotIn('checked_out', columns)

    def test_document_listings_does_not_contain_subdossier_and_checked_out_column(self):
        document_view = self.inbox.restrictedTraverse('tabbedview_view-documents')

        columns = [col.get('column') for col in document_view.columns
                   if isinstance(col, dict)]

        self.assertNotIn('containing_subdossier', columns)
        self.assertNotIn('checked_out', columns)

    def test_documents_listing_only_show_documents_from_the_current_admin_unit(self):
        document_1 =  create(Builder('document')
                             .titled('Doc 1')
                             .within(self.inbox))

        create(Builder('org_unit')
               .id('additional')
               .assign_users([self.user])
               .as_current_org_unit())

        document_2 = create(Builder('document')
                                     .titled('Doc 2')
                                     .within(self.inbox))

        view = self.inbox.restrictedTraverse('tabbedview_view-documents')
        view.update()

        self.assertEquals([document_2],
                          [brain.getObject() for brain in view.contents])


class TestAssignedInboxTaskTab(FunctionalTestCase):

    def setUp(self):
        super(TestAssignedInboxTaskTab, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.inbox = create(Builder('inbox').titled(u'Testinbox'))

    def assert_listing_results(self, viewname, results, ):
        view = self.inbox.restrictedTraverse('tabbedview_view-%s' % (viewname))
        view.update()

        self.assertEquals([task2sqltask(obj) for obj in results],
                          view.contents)

    def test_lists_only_tasks_assigned_to_current_inbox_group(self):
        create_client(clientid='client2')
        assigned_to_inbox_client1 = create(Builder('forwarding')
                            .within(self.inbox)
                            .having(responsible='inbox:client1'))

        create(Builder('forwarding')
                    .within(self.inbox)
                    .having(responsible='inbox:client2'))

        self.assert_listing_results(
            'assigned_inbox_tasks',
            [assigned_to_inbox_client1, ])

    def test_list_tasks_and_forwardings(self):
        task = create(Builder('task')
                      .within(self.inbox)
                      .having(responsible='inbox:client1'))

        forwarding = create(Builder('forwarding')
                            .within(self.inbox)
                            .having(responsible='inbox:client1'))

        self.assert_listing_results(
            'assigned_inbox_tasks', [task, forwarding])


class TestIssuedInboxTaskTab(FunctionalTestCase):

    def setUp(self):
        super(TestIssuedInboxTaskTab, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.inbox = create(Builder('inbox').titled(u'Testinbox'))

    def assert_listing_results(self, viewname, results, ):
        view = self.inbox.restrictedTraverse(
            'tabbedview_view-%s' % (viewname))
        view.update()

        self.assertEquals(results,
                          [brain.getObject() for brain in view.contents])

    def test_list_tasks_and_forwardings(self):
        task = create(Builder('task')
                      .within(self.inbox)
                      .having(issuer='inbox:client1'))

        forwarding = create(Builder('forwarding')
                            .within(self.inbox)
                            .having(issuer='inbox:client1'))

        self.assert_listing_results(
            'issued_inbox_tasks',
            [task, forwarding])

    def test_list_only_task_with_current_inbox_as_issuer(self):
        issued_by_inbox1 = create(Builder('task')
                      .within(self.inbox)
                      .having(issuer='inbox:client1'))

        create(Builder('forwarding')
                            .within(self.inbox)
                            .having(issuer='inbox:client2'))

        self.assert_listing_results(
            'issued_inbox_tasks', [issued_by_inbox1, ])

    def test_list_also_tasks_outside_of_the_inbox(self):
        task_inside = create(Builder('task')
              .within(self.inbox)
              .having(issuer='inbox:client1'))

        task_outside = create(Builder('task')
              .having(issuer='inbox:client1'))

        self.assert_listing_results(
            'issued_inbox_tasks', [task_inside, task_outside])
