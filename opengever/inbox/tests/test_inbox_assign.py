from ftw.builder import Builder
from ftw.builder import create
from opengever.task.adapters import IResponseContainer
from opengever.testing import FunctionalTestCase
from opengever.testing import task2sqltask
from Products.CMFCore.utils import getToolByName


class TestAssingForwarding(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestAssingForwarding, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        create(Builder('org_unit')
               .with_default_groups()
               .having(client_id='client2', title='Client2'))

        self.forwarding = create(
            Builder('forwarding')
            .having(title=u'Test forwarding',
                    responsible_client=u'client1',
                    responsible=u'inbox:client1')
            .in_state('forwarding-state-refused'))

    def test_its_possible_to_select_an_different_client(self):
        self.browser.open(self.forwarding.absolute_url())
        self.browser.getLink('forwarding-transition-reassign-refused').click()

        self.assertItemsEqual(
            ['client1', 'client2'],
            self.browser.control('Responsible Client').options)

    def test_updates_responsible_and_responsible_client(self):
        self.assign_forwarding('client2', 'Fake Response')

        self.assertEquals('client2', self.forwarding.responsible_client)
        self.assertEquals('client2',
                          task2sqltask(self.forwarding).assigned_org_unit)

        self.assertEquals('inbox:client2', self.forwarding.responsible)
        self.assertEquals('inbox:client2',
                          task2sqltask(self.forwarding).responsible)

    def test_assign_sets_forwarding_in_open_state(self):
        self.assign_forwarding('client2', 'Fake Response')

        wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.assertEquals('forwarding-state-open',
                          wf_tool.getInfoFor(self.forwarding, 'review_state'))

        self.assertEquals('forwarding-state-open',
                          task2sqltask(self.forwarding).review_state)

    def test_assign_add_corresonding_response(self):
        self.assign_forwarding('client2', 'Fake Response')

        response = IResponseContainer(self.forwarding)[-1]

        responsible_change = {'id': 'responsible',
                              'name': u'label_responsible',
                              'before': u'inbox:client1',
                              'after': u'inbox:client2'}

        responsible_client_change = {'id': 'responsible_client',
                                     'name': u'label_resonsible_client',
                                     'before': u'client1',
                                     'after': u'client2'}

        self.assertEquals([responsible_change, responsible_client_change],
                          response.changes)

    def assign_forwarding(self, new_client, response):
        self.browser.open(self.forwarding.absolute_url())
        self.browser.getLink('forwarding-transition-reassign-refused').click()

        # select responsible client
        self.browser.getControl('Responsible Client').value = [new_client]

        # select responsible
        self.browser.getControl(
            name='form.widgets.responsible.widgets.query').value = new_client
        self.browser.click('form.widgets.responsible.buttons.search')

        self.browser.getControl('Responsible Client').value = [new_client]
        self.browser.getControl(
            name='form.widgets.responsible:list').value = ['inbox:client2']

        self.browser.fill({'Response': 'Fake response'})
        self.browser.click('Assign')
