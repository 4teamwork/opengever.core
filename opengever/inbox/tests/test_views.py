from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.inbox.testing import OPENGEVER_INBOX_FUNCTIONAL_TESTING
from opengever.ogds.base.utils import get_client_id
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id
from plone.app.testing import logout, login
from plone.app.testing.interfaces import TEST_USER_NAME
from plone.dexterity.utils import createContentInContainer
from zope.component import getUtility


class TestViews(FunctionalTestCase):
    layer = OPENGEVER_INBOX_FUNCTIONAL_TESTING
    use_browser = True

    def setUp(self):
        super(TestViews, self).setUp()
        self.grant('Owner','Editor','Contributor')

        create_client('plone')
        create_client('client2')
        set_current_client_id(self.portal, 'plone')

        create_ogds_user(TEST_USER_NAME)

    def test_views(self):
        # create content:
        inbox = createContentInContainer(self.portal, 'opengever.inbox.inbox', title=u'eingangskorb')
        view = inbox.restrictedTraverse('tabbedview_view-overview')

        createContentInContainer(inbox, 'opengever.document.document',
                                 title=u'Document in inbox')
        createContentInContainer(inbox, 'opengever.document.document',
                                 title=u'Another document in inbox')
        fw1 = createContentInContainer(inbox, 'opengever.inbox.forwarding',
                                       title=u'Forwarding 1',
                                       issuer='inbox:plone',
                                       responsible='inbox:plone',
                                       responsible_client='plone' )
        createContentInContainer(fw1, 'opengever.document.document',
                                 title=u'Document for forwarding')
        createContentInContainer(inbox, 'opengever.inbox.forwarding',
                                 title=u'Another forwarding',
                                 issuer='inbox:client2',
                                 responsible='inbox:client2',
                                 responsible_client='client2' )

        # test documents():
        titles = [doc['Title'] for doc in view.documents()]
        self.assertEquals(titles, ['Document in inbox', 'Another document in inbox'])

        # test assigned_tasks():
        createContentInContainer(self.portal, 'opengever.task.task',
                                 title=u'Task for forwarding',
                                 responsible='inbox:plone',
                                 review_state='task-state-open')

        # change tasks client_id
        principal = 'inbox:%s' % get_client_id()
        query_util = getUtility(ITaskQuery)
        query = query_util._get_tasks_for_responsible_query(principal, 'modified')
        query.filter(Task.title==u'Task for forwarding').all()[0].client_id = 'something_else'

        self.assertEquals(1, len(view.assigned_tasks()))

        # test inbox():
        # change forwardings client_id
        query_util = getUtility(ITaskQuery)
        query = query_util._get_tasks_for_responsible_query(
            principal, 'modified')
        query.filter(Task.title==u'Forwarding 1').all()[0].client_id = 'something_else'

        self.assertEquals(1, len(view.inbox()))

        # test boxes():
        boxes = view.boxes()
        self.assertEquals('documents', boxes[1][0].get('id'))
        self.assertEquals('inbox', boxes[0][0].get('id'))
        self.assertEquals('assigned_tasks', boxes[0][1].get('id'))
        self.assertEquals(2, len(boxes))
        self.assertEquals(2, len(boxes[0]))

        # test GivenTasks:
        given_tasks_view = inbox.restrictedTraverse('tabbedview_view-given_tasks')
        columns = [col.get('column') for col in given_tasks_view.columns if isinstance(col, dict)]
        self.assertNotIn('containing_subdossier', columns)

        # test InboxTrash:
        trash = inbox.restrictedTraverse('tabbedview_view-trash')
        columns = [col.get('column') for col in trash.columns if isinstance(col, dict)]
        self.assertNotIn('containing_subdossier', columns)
        self.assertNotIn('checked_out', columns)

        # test InboxDocuments:
        inbox_docs = inbox.restrictedTraverse('tabbedview_view-documents')
        columns = [col.get('column') for col in inbox_docs.columns if isinstance(col, dict)]
        self.assertNotIn('containing_subdossier', columns)
        self.assertNotIn('checked_out', columns)

        # all actions should not be in enabled_actions
        self.assertIn('create_forwarding', inbox_docs.enabled_actions)
        hidden_actions = ['create_task', 'copy_documents_to_remote_client', 'move_items']
        for action in hidden_actions:
            self.assertNotIn(action, inbox_docs.enabled_actions)

        self.assertIn('create_forwarding', inbox_docs.major_actions)
        self.assertNotIn('create_task', inbox_docs.major_actions)

        # test AccessInboxAllowed:
        logout()
        self.assertEquals(None, inbox.restrictedTraverse('access-inbox-allowed')())
        login(self.portal, TEST_USER_NAME)
        self.assertEquals(1, inbox.restrictedTraverse('access-inbox-allowed')())

        # test InboxAssignedForwardings:
        assigned_fws = inbox.restrictedTraverse('tabbedview_view-assigned_forwardings')
        assigned_fws.sort_order = 'reverse'
        self.assertEquals(1, len(assigned_fws.get_base_query().all()))
