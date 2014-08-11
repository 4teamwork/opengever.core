from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import create_client
from opengever.testing import FunctionalTestCase
from opengever.testing import set_current_client_id
from opengever.testing import task2sqltask


class TestInboxTabs(FunctionalTestCase):

    def setUp(self):
        super(TestInboxTabs, self).setUp()
        self.inbox = create(Builder('inbox').titled(u'Testinbox'))

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


class TestAssignedInboxTaskTab(FunctionalTestCase):

    def setUp(self):
        super(TestAssignedInboxTaskTab, self).setUp()
        create_client()
        set_current_client_id(self.portal)

        self.inbox = create(Builder('inbox').titled(u'Testinbox'))

    def assert_listing_results(self, viewname, results, ):
        view = self.inbox.restrictedTraverse('tabbedview_view-%s' % (viewname))
        view.update()

        self.assertEquals(set([task2sqltask(obj) for obj in results]),
                          set(view.contents))

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
                      .having(responsible='inbox:client1',
                              modification_date=DateTime(2013, 6, 10)))

        forwarding = create(Builder('forwarding')
                            .within(self.inbox)
                            .having(responsible='inbox:client1',
                                    modification_date=DateTime(2013, 6, 11)))

        self.assert_listing_results(
            'assigned_inbox_tasks', [task, forwarding])


class TestIssuedInboxTaskTab(FunctionalTestCase):

    def setUp(self):
        super(TestIssuedInboxTaskTab, self).setUp()
        create_client()
        set_current_client_id(self.portal)

        self.inbox = create(Builder('inbox').titled(u'Testinbox'))

    def assert_listing_results(self, viewname, results, ):
        view = self.inbox.restrictedTraverse(
            'tabbedview_view-%s' % (viewname))
        view.update()

        self.assertEquals(set(results),
                          set([brain.getObject() for brain in view.contents]))

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
              .having(issuer='inbox:client1',
                      modification_date=DateTime(2013, 6, 10)))

        task_outside = create(Builder('task')
              .having(issuer='inbox:client1',
                      modification_date=DateTime(2013, 6, 11)))

        self.assert_listing_results(
            'issued_inbox_tasks', [task_inside, task_outside])
