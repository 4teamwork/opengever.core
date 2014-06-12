from ftw.builder import Builder
from ftw.builder import create
from opengever.globalindex.handlers.task import sync_task
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import task2sqltask

class TestBaseInboxOverview(FunctionalTestCase):

    def setUp(self):
        super(TestBaseInboxOverview, self).setUp()
        self.grant('Owner', 'Editor', 'Contributor')

        self.user1, self.org_unit1, self.admin_unit1 = create(
            Builder('fixture').with_all_unit_setup())

        self.user2, self.org_unit2, self.admin_unit2 = create(
            Builder('fixture')
            .with_user(userid='hans.muster')
            .with_org_unit(client_id=u'client2')
            .with_admin_unit())

        self.inbox = create(Builder('inbox').titled(u'eingangskorb'))
        self.view = self.inbox.restrictedTraverse('tabbedview_view-overview')

class TestInboxOverviewDocumentBox(TestBaseInboxOverview):

    def test_documents_box_list_documents_form_the_inbox(self):
        inbox_document = create(Builder('document')
                                .titled('inbox document')
                                .within(self.inbox))
        create(Builder('document')
               .titled('portal document')
               .within(self.portal))

        self.assert_documents([inbox_document, ], self.view.documents())

    def test_documents_box_list_only_documents_directly_inside_the_inbox(self):
        inbox_document = create(Builder('document')
                                .titled('inbox document')
                                .within(self.inbox))
        forwarding = create(Builder('forwarding').within(self.inbox))
        create(Builder('document')
               .titled('forwarding document')
               .within(forwarding))

        self.assert_documents([inbox_document, ], self.view.documents())

    def test_document_box_is_limited_to_ten_documents(self):
        for i in range(15):
            create(Builder('document').within(self.inbox))

        self.assertEquals(10, len(self.view.documents()))

    def assert_documents(self, expected, value):
        self.assertEquals(
            [obj.Title() for obj in expected],
            [item.get('Title') for item in value])


class TestInboxOverviewAssignedInboxTasks(TestBaseInboxOverview):

    def test_list_tasks_and_forwardings_assigned_to_current_inbox_group(self):
        task = create(Builder('task').having(responsible='inbox:client1'))
        forwarding = create(Builder('forwarding')
                            .having(responsible='inbox:client1'))
        create(Builder('forwarding').having(responsible='inbox:client2'))

        self.assertEquals(
            [task2sqltask(forwarding), task2sqltask(task)],
            self.view.assigned_tasks())

    def test_is_limited_to_five_entries(self):
        for i in range(10):
            create(Builder('forwarding')
                   .having(responsible='inbox:client1'))

        self.assertEquals(5, len(self.view.assigned_tasks()))

    def test_lists_only_the_local_one_when_having_predecessor_successor_couples(self):
        predecessor = create(Builder('forwarding')
                             .having(responsible='inbox:client2',
                                     assigned_client='client2'))
        successor = create(Builder('forwarding')
                           .having(responsible='inbox:client1',
                                   assigned_client='client1')
                           .successor_from(predecessor))

        self.assertEquals(
            [task2sqltask(successor)], self.view.assigned_tasks())

    def test_list_only_active_tasks(self):
        active = create(Builder('forwarding')
                        .having(responsible='inbox:client1'))
        closed = create(Builder('forwarding')
                        .having(responsible='inbox:client1')
                        .in_state('forwarding-state-closed'))
        sync_task(closed, None)

        self.assertEquals(
            [task2sqltask(active)], self.view.assigned_tasks())


class TestInboxOverviewIssuedInboxTasks(TestBaseInboxOverview):

    def test_list_tasks_and_forwardings_issued_by_current_inbox_group(self):
        task = create(Builder('task')
                      .within(self.inbox)
                      .having(issuer='inbox:client1'))
        forwarding = create(Builder('forwarding')
                            .within(self.inbox)
                            .having(issuer='inbox:client1'))
        create(Builder('forwarding').having(issuer='inbox:client2'))

        self.assertEquals(
            [task, forwarding],
            [brain.getObject() for brain in self.view.issued_tasks()])

    def test_is_limited_to_five_entries(self):
        for i in range(10):
            create(Builder('forwarding')
                   .within(self.inbox)
                   .having(issuer='inbox:client1'))

        self.assertEquals(5, len(self.view.issued_tasks()))

    def test_list_only_active_tasks_and_forwardings(self):
        active = create(Builder('forwarding')
                        .within(self.inbox)
                        .having(issuer='inbox:client1'))

        closed = create(Builder('forwarding')
                        .within(self.inbox)
                        .having(issuer='inbox:client1')
                        .in_state('forwarding-state-closed'))
        self.assertEquals(
            [active, ],
            [brain.getObject() for brain in self.view.issued_tasks()])
