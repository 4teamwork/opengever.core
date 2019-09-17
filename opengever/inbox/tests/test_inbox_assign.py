from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.base.response import IResponseContainer
from opengever.testing import FunctionalTestCase
from Products.CMFCore.utils import getToolByName
from sqlalchemy import desc


class TestAssignForwarding(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestAssignForwarding, self).setUp()

        create(Builder('org_unit')
               .with_default_groups()
               .id('org-unit-2')
               .having(title='Org Unit 2',
                       admin_unit=self.admin_unit))

        self.forwarding = create(
            Builder('forwarding')
            .having(title=u'Test forwarding',
                    responsible_client=u'org-unit-1',
                    responsible=u'inbox:org-unit-1')
            .in_state('forwarding-state-refused'))

    @browsing
    def test_updates_responsible_and_responsible_client(self, browser):
        self.assign_forwarding('org-unit-2', 'Fake Response')

        self.assertEquals('org-unit-2', self.forwarding.responsible_client)
        self.assertEquals('org-unit-2',
                          self.forwarding.get_sql_object().assigned_org_unit)

        self.assertEquals('inbox:org-unit-2', self.forwarding.responsible)
        self.assertEquals('inbox:org-unit-2',
                          self.forwarding.get_sql_object().responsible)

    @browsing
    def test_assign_sets_forwarding_in_open_state(self, browser):
        self.assign_forwarding('org-unit-2', 'Fake Response')

        wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.assertEquals('forwarding-state-open',
                          wf_tool.getInfoFor(self.forwarding, 'review_state'))

        self.assertEquals('forwarding-state-open',
                          self.forwarding.get_sql_object().review_state)

    @browsing
    def test_assign_add_corresonding_response(self, browser):
        self.assign_forwarding('org-unit-2', 'Fake Response')

        response = IResponseContainer(self.forwarding).list()[-1]

        responsible_change = {'field_id': 'responsible',
                              'field_title': u'label_responsible',
                              'before': u'inbox:org-unit-1',
                              'after': u'inbox:org-unit-2'}

        responsible_client_change = {'field_id': 'responsible_client',
                                     'field_title': u'label_resonsible_client',
                                     'before': u'org-unit-1',
                                     'after': u'org-unit-2'}

        self.assertEquals([responsible_change, responsible_client_change],
                          response.changes)

    @browsing
    def test_activity_is_recorded_correctly(self, browser):
        self.assign_forwarding('org-unit-2', 'Fake Response')

        self.assertEquals('org-unit-2', self.forwarding.responsible_client)
        self.assertEquals('org-unit-2',
                          self.forwarding.get_sql_object().assigned_org_unit)

        self.assertEquals('inbox:org-unit-2', self.forwarding.responsible)
        self.assertEquals('inbox:org-unit-2',
                          self.forwarding.get_sql_object().responsible)

        self.assertEquals(
            'forwarding-transition-reassign-refused',
            Activity.query.order_by(desc(Activity.id)).first().kind)

    def assign_forwarding(self, new_client, response, browser=default_browser):
        browser.login().open(self.forwarding)
        browser.click_on('forwarding-transition-reassign-refused')
        browser.fill({'Response': 'Fake response'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('inbox:' + new_client)

        browser.click_on('Assign')
