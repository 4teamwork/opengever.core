from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.inbox.yearfolder import get_current_yearfolder
from opengever.task.adapters import IResponseContainer
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

        response = IResponseContainer(forwarding)[-1]
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

        response = IResponseContainer(forwarding)[-1]
        task = self.empty_dossier.objectValues()[-1]
        self.assertEqual(
            'forwarding-transition-assign-to-dossier', response.transition)
        self.assertEqual(Oguid.for_object(task).id, response.successor_oguid)

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

        response = IResponseContainer(self.inbox_forwarding)[-1]
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

        response = IResponseContainer(self.inbox_forwarding)[-1]
        self.assertEqual(u'Robert macht das.', response.text)
        self.assertEqual('forwarding-transition-reassign-refused', response.transition)
