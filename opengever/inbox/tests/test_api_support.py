from ftw.testbrowser import browsing
from opengever.inbox.yearfolder import get_current_yearfolder
from opengever.task.adapters import IResponseContainer
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestAPITransitions(IntegrationTestCase):

    api_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

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
