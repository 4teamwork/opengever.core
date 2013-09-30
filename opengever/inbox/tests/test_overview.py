from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id
from opengever.testing.helpers import obj2brain
from opengever.testing.helpers import task2sqltask
from plone.app.testing.interfaces import TEST_USER_NAME


class TestInboxOverviewDocumentBox(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestInboxOverviewDocumentBox, self).setUp()
        self.grant('Owner', 'Editor', 'Contributor')

        self.inbox = create(Builder('inbox').titled(u'eingangskorb'))
        self.view = self.inbox.restrictedTraverse('tabbedview_view-overview')

    def test_documents_box_list_documents_form_the_inbox(self):
        inbox_document = create(Builder('document').within(self.inbox))
        create(Builder('document').within(self.portal))

        self.assert_documents([inbox_document, ], self.view.documents())

    def test_documents_box_list_only_documents_directly_inside_the_inbox(self):
        inbox_document = create(Builder('document').within(self.inbox))
        forwarding = create(Builder('forwarding').within(self.inbox))
        create(Builder('document').within(forwarding))

        self.assert_documents([inbox_document, ], self.view.documents())

    def test_document_box_is_limited_to_ten_documents(self):
        for i in range(15):
            create(Builder('document').within(self.inbox))

        self.assertEquals(10, len(self.view.documents()))

    def assert_documents(self, expected, value):

        self.assertEquals(
            [obj.Title() for obj in expected],
            [item.get('Title') for item in value])


class TestInboxOverviewAssignedInboxTasks(TestInboxOverviewDocumentBox):

    def setUp(self):
        super(TestInboxOverviewAssignedInboxTasks, self).setUp()

        create_client('client1')
        create_client('client2')
        set_current_client_id(self.portal, 'client1')

        create_ogds_user(TEST_USER_NAME)

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


class TestInboxOverviewIssuedInboxTasks(TestInboxOverviewDocumentBox):

    def setUp(self):
        super(TestInboxOverviewIssuedInboxTasks, self).setUp()

        create_client('client1')
        create_client('client2')
        set_current_client_id(self.portal, 'client1')

        create_ogds_user(TEST_USER_NAME)

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
