from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from opengever.inbox.browser.refuse import ForwardingRefuseForm
from opengever.inbox.browser.refuse import STATUS_ALLREADY_DONE
from opengever.inbox.browser.refuse import STATUS_SUCCESSFULL
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.transport import REQUEST_KEY
from opengever.task.adapters import IResponseContainer
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import obj2brain
from opengever.testing.helpers import task2sqltask
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
import json


class TestRefusingForwardings(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestRefusingForwardings, self).setUp()

        user = create(Builder('ogds_user'))

        client1 = create(Builder('org_unit')
                         .having(client_id=u'client1')
                         .assign_users([user], create_inbox=False)
                         .as_current_org_unit())

        client2 = create(Builder('org_unit')
                         .having(client_id=u'client2')
                         .assign_users([user], create_group=False))

        admin_unit = create(Builder('admin_unit')
                            .wrapping_org_unit(client1)
                            .as_current_admin_unit())

        self.forwarding = create(Builder('forwarding')
                            .having(
                                title=u'Test forwarding',
                                responsible_client=u'client2',
                                responsible=u'inbox:client2'))

        # TODO: mock remote_request instead of patching
        # the store_copy_in_remote_yearfolder and test this functionality
        # ass well
        def fake_copy(self, refusing_client_id):
            return ''

        ForwardingRefuseForm.store_copy_in_remote_yearfolder = fake_copy

    def refuse_a_forwarding(self, forwarding, response):
        self.browser.open(forwarding.absolute_url())
        self.browser.getLink('forwarding-transition-refuse').click()

        self.browser.fill({'Response': response})
        self.browser.click('Refuse')

    def test_set_forwarding_in_refused_state(self):
        self.refuse_a_forwarding(self.forwarding, 'That is not my problem')

        wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.assertEquals(
            'forwarding-state-refused',
            wf_tool.getInfoFor(self.forwarding, 'review_state'))

    def test_resets_responsible_to_the_issuing_client_inbox(self):
        self.refuse_a_forwarding(self.forwarding, 'That is not my problem')

        self.assertEquals('client1', self.forwarding.responsible_client)
        self.assertEquals('inbox:client1', self.forwarding.responsible)

    def test_appends_an_correspondent_response(self):
        self.refuse_a_forwarding(self.forwarding, 'That is not my problem')

        response = IResponseContainer(self.forwarding)[-1]
        self.assertEquals('That is not my problem', response.text)
        self.assertEquals('forwarding-transition-refuse', response.transition)


class TestRefuseForwardingStoring(FunctionalTestCase):

    def setUp(self):
        super(TestRefuseForwardingStoring, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture')
            .with_user()
            .with_org_unit()
            .with_admin_unit())
        create(Builder('org_unit').having(client_id='client2')
                                  .assign_users([self.user]))

        self.inbox = create(Builder('inbox'))
        self.forwarding = create(Builder('forwarding')
                                 .within(self.inbox)
                                 .having(
                                     title=u'Test forwarding',
                                     responsible_client=u'client2',
                                     responsible=u'inbox:client2'))

    def test_refuse_create_task_in_actual_yearfolder(self):
        status, copy = self.refuse_forwarding(self.forwarding)

        self.assertEquals('Test forwarding', copy.title)
        self.assertEquals('client2', copy.responsible_client)
        self.assertEquals('inbox:client2', copy.responsible)

    def test_refuse_set_task_copy_in_closed_state(self):
        wftool = getToolByName(self.portal, 'portal_workflow')
        status, copy = self.refuse_forwarding(self.forwarding)

        self.assertEquals('forwarding-state-closed',
                          wftool.getInfoFor(copy, 'review_state'))
        self.assertEquals('forwarding-state-closed',
                          obj2brain(copy).review_state)
        self.assertEquals('forwarding-state-closed',
                          task2sqltask(copy).review_state)

    def test_refusing_multiple_times_creates_only_one_forwarding(self):
        self.refuse_forwarding(self.forwarding)
        self.refuse_forwarding(self.forwarding)

        yeafolder = self.inbox.get(str(datetime.now().year))
        self.assertEquals(1, len(yeafolder.getFolderContents()),
                          'The forwarding was copied multiple times,'
                          ' the already_done check works not correctly.')

    def test_successfull_refusing_returns_task_path_and_status_successfull(self):
        status, copy = self.refuse_forwarding(self.forwarding)

        self.assertEquals(STATUS_SUCCESSFULL, status)

    def test_multiple_refusing_call_returns_task_path_already_done_status(self):
        self.refuse_forwarding(self.forwarding)
        status, copy = self.refuse_forwarding(self.forwarding)

        self.assertEquals(STATUS_ALLREADY_DONE, status)

    def refuse_forwarding(self, forwarding):
        transporter = getUtility(ITransporter)
        self.portal.REQUEST.set(REQUEST_KEY,
                                transporter.extract(forwarding))
        self.portal.REQUEST.set('review_state', 'forwarding-state-refused')
        response = self.portal.unrestrictedTraverse('store_refused_forwarding')()
        response = json.loads(response)

        if response.get('remote_task'):
            copy = self.portal.restrictedTraverse(
                response.get('remote_task').encode('utf-8'))
        else:
            copy = None
        return response.get('status'), copy
