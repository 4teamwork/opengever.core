from datetime import datetime
from ftw.testing import MockTestCase
from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.task.browser.accept.utils import accept_forwarding_with_successor
from opengever.task.testing import OPENGEVER_TASK_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from opengever.task.tests.data import DOCUMENT_EXTRACTION, INBOX_EXTRACTION

FAKE_INTID = '711567936'


class FakeResponse(object):
    def __init__(self, result):
        self.result = result

    def read(self):
        return self.result


class TestTaskAccepting(MockTestCase):

    layer = OPENGEVER_TASK_INTEGRATION_TESTING




    def setUp(self):
        self.portal = self.layer.get('portal')

        self.fake_inbox = 'FAKE'

        self.inbox = createContentInContainer(
            self.portal, 'opengever.inbox.inbox', title=u'inbox')

        self.dossier = createContentInContainer(
            self.portal, 'opengever.dossier.businesscasedossier', title=u'inbox')


    def test_accept_forwarding_with_successor_with_dossier(self):

        # create fake predecessor
        predecessor = Task(FAKE_INTID, 'client2')
        predecessor.physical_path = 'eingangskorb/forwarding-1'
        predecessor.issuer = 'testuser2'
        predecessor.responsible_client = 'plone'
        predecessor.responsible = TEST_USER_ID
        predecessor.deadline = datetime.now()

        remote_request = self.mocker.replace('opengever.ogds.base.utils.remote_request')

        self.expect(remote_request(
                'client2', '@@transporter-extract-object-json',
                path='eingangskorb/forwarding-1',
                data={},
                headers={})).result(FakeResponse(INBOX_EXTRACTION))

        self.expect(remote_request(
                'client2', '@@task-documents-extract',
                path='eingangskorb/forwarding-1',
                data={'documents': 'null'},
                headers={})).result(FakeResponse(DOCUMENT_EXTRACTION))

        self.replay()

        session = Session()
        session.add(predecessor)

        accept_forwarding_with_successor(
            self.portal,
            'client2:%s' % FAKE_INTID,
            u'This is a message',
            dossier=self.dossier)

    #     context = self.stub()

    #     forwarding = self.stub()
    #     self.expect(forwarding.client_id).result('client-1')
    #     self.expect(forwarding.physical_path).result('/platform/inbox-1/task-1')

    #     # TaskQuery utility
    #     task_query = self.stub()
    #     self.mock_utility(task_query, ITaskQuery)
    #     self.expect(task_query.get_task_by_oguid('og_1')).result(forwarding)

    #     successor = self.stub()
    #     self.expect(setattr(forwarding, 'issuer', 'inbox_group_client_2'))
    #     # self.expect(forwarding.physical_path).result('/platform/inbox-1/task-1')

    #     catalog = self.stub()
    #     inbox = self.stub()
    #     self.mock_tool(catalog, 'portal_catalog')
    #     self.expect(catalog(portal_type="opengever.inbox.inbox")).result([inbox, ])
    #     self.expect(inbox.getObject()).result(inbox)

    #     transporter = self.stub()
    #     self.mock_utility(transporter, ITransporter)
    #     self.expect(
    #         transporter.transport_from(
    #             inbox, 'client-1', '/platform/inbox-1/task-1')).result(successor)

    #     client = self.stub()
    #     self.expect(client.inbox_group.id).result('inbox_group_client_2')
    #     get_current_client = self.mocker.replace(
    #         'opengever.ogds.base.utils.get_current_client')
    #     self.expect(get_current_client()).result(client)


    #     # yearfolder = self.stub()
    #     # self.expect(inbox.get(ANY)).result(yearfolder)

    #     self.replay()

    #     accept_forwarding_with_successor(context, 'og_1', 'FAKE respone text')
