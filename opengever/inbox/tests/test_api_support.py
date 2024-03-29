from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from mock import patch
from mock import PropertyMock
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseContainer
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.inbox.yearfolder import _create_yearfolder
from opengever.inbox.yearfolder import get_current_yearfolder
from opengever.ogds.base.ou_selector import CURRENT_ORG_UNIT_KEY
from opengever.task.browser.accept.utils import FORWARDING_SUCCESSOR_TYPE
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from plone import api
import json


class TestAPITransitions(IntegrationTestCase):

    @browsing
    def test_close_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)

        url = '{}/@workflow/forwarding-transition-close'.format(
            self.inbox_forwarding.absolute_url())

        data = {'text': 'Wird gemacht.'}
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        yearfolder = get_current_yearfolder(context=self.inbox)
        self.assertEqual(1, len(yearfolder.objectValues()))

        forwarding = yearfolder.objectValues()[0]
        self.assertEqual(
            'forwarding-state-closed', api.content.get_state(forwarding))

        response = IResponseContainer(forwarding).list()[-1]
        self.assertEqual('Wird gemacht.', response.text)
        self.assertEqual('forwarding-transition-close', response.transition)

    @browsing
    def test_assign_to_dossier_stores_and_close_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)

        url = '{}/@workflow/forwarding-transition-assign-to-dossier'.format(
            self.inbox_forwarding.absolute_url())

        dossier_uid = obj2brain(self.empty_dossier).UID
        data = {'dossier': dossier_uid}
        browser.open(url, method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        yearfolder = get_current_yearfolder(context=self.inbox)
        self.assertEqual(1, len(yearfolder.objectValues()))

        forwarding = yearfolder.objectValues()[0]
        self.assertEqual(
            'forwarding-state-closed', api.content.get_state(forwarding))

        response = IResponseContainer(forwarding).list()[-1]
        task = self.empty_dossier.objectValues()[-1]
        self.assertEqual(
            'forwarding-transition-assign-to-dossier', response.transition)
        self.assertEqual(Oguid.for_object(task).id, response.successor_oguid)

    @browsing
    def test_assign_to_dossier_validates_add_permission(self, browser):
        self.login(self.secretariat_user, browser=browser)

        url = '{}/@workflow/forwarding-transition-assign-to-dossier'.format(
            self.inbox_forwarding.absolute_url())

        self.dossier.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.dossier).add_or_update_assignment(
            SharingRoleAssignment(api.user.get_current().getId(), ['Reader']))

        dossier_uid = obj2brain(self.dossier).UID
        data = {'dossier': dossier_uid}

        self.assertFalse(api.user.has_permission('opengever.task: Add task', obj=self.dossier))
        with browser.expect_http_error(401):
            browser.open(url, method='POST',
                         data=json.dumps(data), headers=self.api_headers)

    @browsing
    def test_assign_to_dossier_validates_addable_types(self, browser):
        self.login(self.secretariat_user, browser=browser)

        url = '{}/@workflow/forwarding-transition-assign-to-dossier'.format(
            self.inbox_forwarding.absolute_url())

        self.assertTrue(api.user.has_permission('opengever.task: Add task', obj=self.dossier))
        dossier_uid = obj2brain(self.inactive_dossier).UID
        data = {'dossier': dossier_uid}

        with browser.expect_http_error(401):
            browser.open(url, method='POST',
                         data=json.dumps(data), headers=self.api_headers)

    @browsing
    def test_assign_to_dossier_open_successor_task(self, browser):
        self.login(self.secretariat_user, browser=browser)

        url = '{}/@workflow/forwarding-transition-assign-to-dossier'.format(
            self.inbox_forwarding.absolute_url())

        dossier_uid = obj2brain(self.empty_dossier).UID
        data = {'dossier': dossier_uid}
        browser.open(url, method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        task = self.empty_dossier.objectValues()[-1]

        self.assertEqual(FORWARDING_SUCCESSOR_TYPE, task.task_type)
        self.assertEqual('inbox:fa', task.issuer)
        self.assertEqual(u'F\xf6rw\xe4rding', task.title)

    @browsing
    def test_assign_to_dossier_allows_to_pass_task_data_which_will_be_used_to_create_the_new_task(self, browser):
        self.login(self.secretariat_user, browser=browser)

        url = '{}/@workflow/forwarding-transition-assign-to-dossier'.format(
            self.inbox_forwarding.absolute_url())

        dossier_uid = obj2brain(self.empty_dossier).UID
        data = {
            'dossier': dossier_uid,
            'task': {
                u'title': u'My custom task',
                u'task_type': u'information',
                u'deadline': u'2016-11-01',
                u'is_private': False,
                u'responsible': u'robert.ziegler',
                u'responsible_client': u'fa',
                u'revoke_permissions': True,
                u'issuer': u'robert.ziegler'}}

        browser.open(url, method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        task = self.empty_dossier.objectValues()[-1]

        self.assertEqual(FORWARDING_SUCCESSOR_TYPE, task.task_type)
        self.assertEqual(u'robert.ziegler', task.issuer)
        self.assertEqual(u'My custom task', task.title)

    @browsing
    def test_reassign_forwarding(self, browser):
        self.login(self.administrator, browser=browser)

        # self.add_additional_org_unit()
        url = '{}/@workflow/forwarding-transition-reassign'.format(
            self.inbox_forwarding.absolute_url())

        # missing responsible
        data = {'text': 'Wird gemacht.'}
        with browser.expect_http_error(400):
            browser.open(url, method='POST',
                         data=json.dumps(data), headers=self.api_headers)

        # working
        data = {'text': 'Robert macht das.',
                'responsible': 'james.bond',
                'responsible_client': u'rk'}
        browser.open(url, method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual('james.bond',
                         self.inbox_forwarding.responsible)
        self.assertEqual('rk',
                         self.inbox_forwarding.responsible_client)
        self.assertEqual('forwarding-state-open',
                         api.content.get_state(self.inbox_forwarding))

        response = IResponseContainer(self.inbox_forwarding).list()[-1]
        self.assertEqual(u'Robert macht das.', response.text)
        self.assertEqual('forwarding-transition-reassign', response.transition)

    @browsing
    def test_reassign_refused_forwarding(self, browser):
        self.login(self.administrator, browser=browser)
        self.set_workflow_state(
            'forwarding-state-refused', self.inbox_forwarding)

        url = '{}/@workflow/forwarding-transition-reassign-refused'.format(
            self.inbox_forwarding.absolute_url())

        # missing responsible
        data = {'text': 'Wird gemacht.'}
        with browser.expect_http_error(400):
            browser.open(url, method='POST',
                         data=json.dumps(data), headers=self.api_headers)

        # working
        data = {'text': 'Robert macht das.',
                'responsible': self.dossier_responsible.id,
                'responsible_client': u'fa'}
        browser.open(url, method='POST',
                     data=json.dumps(data), headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(self.dossier_responsible.id,
                         self.inbox_forwarding.responsible)

        self.assertEqual('forwarding-state-open',
                         api.content.get_state(self.inbox_forwarding))

        response = IResponseContainer(self.inbox_forwarding).list()[-1]
        self.assertEqual(u'Robert macht das.', response.text)
        self.assertEqual('forwarding-transition-reassign-refused', response.transition)

    @browsing
    def test_refuse_forwarding(self, browser):
        self.login(self.secretariat_user, browser)

        # set rk as current org unit
        driver = browser.get_driver()
        driver.requests_session.cookies.set(CURRENT_ORG_UNIT_KEY, 'rk')

        forwarding = create(Builder('forwarding')
                            .within(self.inbox_rk)
                            .titled(u'F\xf6rw\xe4rding')
                            .having(responsible_client='fa',
                                    responsible='inbox:fa',
                                    issuer='inbox:rk'))

        doc_in_forwarding = create(Builder('document').within(forwarding)
                                   .titled(u'Dokument im Eingangsk\xf6rbliweiterleitung')
                                   .with_asset_file('text.txt'))

        local_url = '{}/@workflow/forwarding-transition-refuse'.format(
            forwarding.absolute_url())

        # patch is_assigned_to_current_admin_unit so that refuse transition is allowed
        with patch('opengever.task.browser.transitioncontroller.TaskChecker.'
                   'is_assigned_to_current_admin_unit',
                   new_callable=PropertyMock) as mock_is_assigned_to_current_admin_unit:
            mock_is_assigned_to_current_admin_unit.return_value = False

            # patch get:yearfolder, since yearfolder depends on current admin unit
            # which is set to rk
            yearfolder = _create_yearfolder(self.inbox, str(datetime.now().year))
            with patch('opengever.inbox.browser.refuse.StoreRefusedForwardingView.get_yearfolder'
                       ) as mock_get_yearfolder:
                mock_get_yearfolder.return_value = yearfolder

                browser.open(local_url, method='POST',
                             data=json.dumps({'text': "I don't want to do this"}),
                             headers=self.api_headers)

        url = browser.json['transition_response']['location']
        path = url.split('nohost')[-1].encode('utf-8')
        copied_forwarding = api.portal.get().restrictedTraverse(path)

        self.assertEqual('inbox:rk', forwarding.issuer)
        self.assertEqual('inbox:rk', copied_forwarding.issuer)

        self.assertEqual('inbox:rk', forwarding.responsible)
        self.assertEqual('inbox:fa', copied_forwarding.responsible)
        self.assertEqual(['inbox:fa'], forwarding.get_former_responsibles())

        self.assertEqual('forwarding-state-refused', api.content.get_state(forwarding))
        self.assertEqual('forwarding-state-closed', api.content.get_state(copied_forwarding))

        self.assertEqual('opengever.inbox.yearfolder', copied_forwarding.aq_parent.portal_type)

        doc_in_copied_forwarding = copied_forwarding.objectValues()[0]
        self.assertEqual(doc_in_forwarding.title, doc_in_copied_forwarding.title)

        self.assertIn("I don't want to do this",
                      [response.text for response in IResponseContainer(forwarding).list()])

        self.assertIn("I don't want to do this",
                      [response.text for response in IResponseContainer(copied_forwarding).list()])
