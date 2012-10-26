from Products.CMFCore.utils import getToolByName
from datetime import datetime
from ftw.testing import MockTestCase
from mocker import ANY
from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.task.adapters import IResponseContainer
from opengever.task.browser.accept.utils import accept_forwarding_with_successor
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.testing import OPENGEVER_TASK_INTEGRATION_TESTING
from opengever.task.tests.data import DOCUMENT_EXTRACTION, FORWARDING_EXTRACTION
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


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
                headers={})).result(FakeResponse(FORWARDING_EXTRACTION))

        self.expect(remote_request(
                'client2', '@@task-documents-extract',
                path='eingangskorb/forwarding-1',
                data={'documents': 'null'},
                headers={})).result(FakeResponse(DOCUMENT_EXTRACTION))

        # TODO replace any with the realy expected data
        self.expect(remote_request(
                'client2', '@@task-responses-extract',
                path='eingangskorb/forwarding-1',
                data=ANY)).result(FakeResponse('[]'))

        self.expect(remote_request(
                'client2', '@@store_forwarding_in_yearfolder',
                path='eingangskorb/forwarding-1',
                # data={'response_text': 'This is a message',
                #       'successor_oguid': u'plone:1231066935',
                #       'transition': 'forwarding-transition-accept'}
                data=ANY,
                )).result(FakeResponse('OK'))

        self.replay()


        wft = getToolByName(self.portal, 'portal_workflow')
        intids = getUtility(IIntIds)


        session = Session()
        session.add(predecessor)

        accept_forwarding_with_successor(
            self.portal,
            'client2:%s' % FAKE_INTID,
            u'This is a message',
            dossier=self.dossier)

        # CHECKS
        # ---------------------
        # yearfolder:
        yearfolder = self.inbox.get(str(datetime.now().year), None)
        self.assertTrue(yearfolder)
        self.assertEquals(yearfolder.title, u'Closed 2012')

        # forwarding ...
        # is stored in the yearfolder
        forwarding = yearfolder.get('forwarding-1', None)
        self.assertTrue(forwarding)

        # and closed
        self.assertEquals(wft.getInfoFor(forwarding, 'review_state'),
                          'forwarding-state-closed')

        # attributes are correctly moved
        self.assertEquals(forwarding.responsible, u'inbox:plone')

        # the issuer should be changed to the local inbox group
        self.assertEquals(forwarding.issuer, u'inbox:plone')

        # also the response is correctly added
        response = IResponseContainer(forwarding)[0]
        self.assertEquals(response.transition, 'forwarding-transition-accept')

        # task (succesor of the forwarding)
        task = self.dossier.get('task-1')
        self.assertTrue(task)
        self.assertEquals(
            ISuccessorTaskController(forwarding).get_successors()[0].int_id,
            intids.getId(task))

        # the succesor link is also in the response correctly
        self.assertEquals(
            response.successor_oguid,
            ISuccessorTaskController(task).get_oguid())
