from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.task.adapters import IResponseContainer
from opengever.testing import FunctionalTestCase
from Products.CMFCore.utils import getToolByName


class TestAssingForwarding(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestAssingForwarding, self).setUp()

        create(Builder('org_unit')
               .with_default_groups()
               .id('client2')
               .having(title='Client2',
                       admin_unit=self.admin_unit))

        self.forwarding = create(
            Builder('forwarding')
            .having(title=u'Test forwarding',
                    responsible_client=u'client1',
                    responsible=u'inbox:client1')
            .in_state('forwarding-state-refused'))

    @browsing
    def test_updates_responsible_and_responsible_client(self, browser):
        self.assign_forwarding('client2', 'Fake Response')

        self.assertEquals('client2', self.forwarding.responsible_client)
        self.assertEquals('client2',
                          self.forwarding.get_sql_object().assigned_org_unit)

        self.assertEquals('inbox:client2', self.forwarding.responsible)
        self.assertEquals('inbox:client2',
                          self.forwarding.get_sql_object().responsible)

    @browsing
    def test_assign_sets_forwarding_in_open_state(self, browser):
        self.assign_forwarding('client2', 'Fake Response')

        wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.assertEquals('forwarding-state-open',
                          wf_tool.getInfoFor(self.forwarding, 'review_state'))

        self.assertEquals('forwarding-state-open',
                          self.forwarding.get_sql_object().review_state)

    @browsing
    def test_assign_add_corresonding_response(self, browser):
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

    @browsing
    def test_activity_is_recorded_correctly(self, browser):
        self.assign_forwarding('client2', 'Fake Response')

        self.assertEquals('client2', self.forwarding.responsible_client)
        self.assertEquals('client2',
                          self.forwarding.get_sql_object().assigned_org_unit)

        self.assertEquals('inbox:client2', self.forwarding.responsible)
        self.assertEquals('inbox:client2',
                          self.forwarding.get_sql_object().responsible)

        self.assertEquals(1, len(Activity.query.all()))
        self.assertEquals('forwarding-transition-reassign-refused',
                          Activity.query.all()[0].kind)

    def assign_forwarding(self, new_client, response, browser=default_browser):
        browser.login().open(self.forwarding)
        browser.click_on('forwarding-transition-reassign-refused')
        browser.fill({'Response': 'Fake response'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('inbox:' + new_client)

        browser.click_on('Assign')
