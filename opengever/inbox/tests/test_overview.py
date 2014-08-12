from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from opengever.globalindex.handlers.task import sync_task
from opengever.testing import FunctionalTestCase


class TestBaseInboxOverview(FunctionalTestCase):

    def setUp(self):
        super(TestBaseInboxOverview, self).setUp()
        self.grant('Owner', 'Editor', 'Contributor')

        self.user2, self.org_unit2, self.admin_unit2 = create(
            Builder('fixture')
            .with_user(userid='hans.muster')
            .with_org_unit(client_id=u'client2')
            .with_admin_unit())

        self.inbox = create(Builder('inbox').titled(u'eingangskorb'))
        self.view = self.inbox.restrictedTraverse('tabbedview_view-overview')


class TestInboxOverviewDocumentBox(TestBaseInboxOverview):

    def list_documents_from_the_inbox(self):
        inbox_document = create(Builder('document')
                                .titled('inbox document')
                                .within(self.inbox))
        create(Builder('document')
               .titled('portal document')
               .within(self.portal))

        self.assert_documents([inbox_document, ], self.view.documents())

    def test_list_only_documents_directly_inside_the_current_inbox(self):
        inbox_document = create(Builder('document')
                                .titled('inbox document')
                                .within(self.inbox))
        forwarding = create(Builder('forwarding').within(self.inbox))
        create(Builder('document')
               .titled('forwarding document')
               .within(forwarding))

        self.assert_documents([inbox_document, ], self.view.documents())

    def test_list_only_documents_in_the_current_inbox(self):
        sub_inbox_1 = create(Builder('inbox')
                             .within(self.inbox)
                             .having(responsible_org_unit='client1'))

        sub_inbox_2 = create(Builder('inbox')
                             .within(self.inbox)
                             .having(responsible_org_unit='client2'))

        doc1 = create(Builder('document')
                       .titled('Doc 1').within(sub_inbox_1))
        doc2 = create(Builder('document')
                       .titled('Doc 2').within(sub_inbox_2))

        sub_inbox_1_view = sub_inbox_1.restrictedTraverse(
            'tabbedview_view-overview')

        self.assert_documents([doc1, ], sub_inbox_1_view.documents())

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
        task = create(Builder('task')
                      .with_modification_date(DateTime(2014, 1, 1))
                      .having(responsible='inbox:client1'))
        forwarding = create(Builder('forwarding')
                            .with_modification_date(DateTime(2014, 1, 2))
                            .having(responsible='inbox:client1'))
        create(Builder('forwarding').having(responsible='inbox:client2'))

        self.assertEquals(
            [forwarding.get_sql_object(), task.get_sql_object()],
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
            [successor.get_sql_object()], self.view.assigned_tasks())

    def test_list_only_active_tasks(self):
        active = create(Builder('forwarding')
                        .having(responsible='inbox:client1'))
        closed = create(Builder('forwarding')
                        .having(responsible='inbox:client1')
                        .in_state('forwarding-state-closed'))
        sync_task(closed, None)

        self.assertEquals(
            [active.get_sql_object()],
            self.view.assigned_tasks())

    def test_is_sorted_on_modification_date_last_modified_first(self):
        task1 = create(Builder('task')
                       .with_modification_date(DateTime(2014, 1, 2))
                       .having(responsible='inbox:client1'))

        task2 = create(Builder('task')
                       .with_modification_date(DateTime(2014, 1, 1))
                       .having(responsible='inbox:client1'))

        task3 = create(Builder('task')
                      .with_modification_date(DateTime(2014, 1, 3))
                      .having(responsible='inbox:client1'))

        self.assertEquals(
            [task.get_sql_object() for task in [task3, task1, task2]],
            self.view.assigned_tasks())


class TestInboxOverviewIssuedInboxTasks(TestBaseInboxOverview):

    def test_list_tasks_and_forwardings_issued_by_current_inbox_group(self):
        task = create(Builder('task')
                      .with_modification_date(DateTime(2014, 1, 1))
                      .within(self.inbox)
                      .having(issuer='inbox:client1'))
        forwarding = create(Builder('forwarding')
                            .with_modification_date(DateTime(2014, 2, 1))
                            .within(self.inbox)
                            .having(issuer='inbox:client1'))
        create(Builder('forwarding').having(issuer='inbox:client2'))

        self.assertEquals(
            [forwarding.get_sql_object(), task.get_sql_object()],
            self.view.issued_tasks())

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

        create(Builder('forwarding')
               .within(self.inbox)
               .having(issuer='inbox:client1')
               .in_state('forwarding-state-closed'))

        self.assertEquals(
            [active.get_sql_object()],
            self.view.issued_tasks())

    def test_is_sorted_by_modfied(self):
        task1 = create(Builder('task')
                       .with_modification_date(DateTime(2014, 1, 2))
                       .having(issuer='inbox:client1'))

        task2 = create(Builder('task')
                       .with_modification_date(DateTime(2014, 1, 1))
                       .having(issuer='inbox:client1'))

        task3 = create(Builder('task')
                      .with_modification_date(DateTime(2014, 1, 3))
                      .having(issuer='inbox:client1'))

        self.assertEquals(
            [task.get_sql_object() for task in [task3, task1, task2]],
            self.view.issued_tasks())
