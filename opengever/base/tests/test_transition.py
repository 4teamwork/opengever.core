from ftw.testbrowser import browsing
from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.testing import IntegrationTestCase
from plone import api
from zope.interface.verify import verifyClass
from zope.schema._bootstrapinterfaces import WrongType
import json


class TestTransitionExtender(IntegrationTestCase):

    def test_implements_interface(self):
        verifyClass(ITransitionExtender, TransitionExtender)

    def test_raises_validation_error_when_called_invalid_via_python_api(self):
        self.login(self.dossier_responsible)

        wftool = api.portal.get_tool('portal_workflow')
        with self.assertRaises(WrongType):
            wftool.doActionFor(self.task, 'task-transition-modify-deadline',
                               transition_params={'new_deadline':'XYZ'})

    @browsing
    def test_raises_badrequest_when_called_invalid_via_rest_api(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        url = '{}/@workflow/task-transition-modify-deadline'.format(
            self.task.absolute_url())

        data = {'text': 'Deadline change!', 'new_deadline': 'not-valid'}
        with browser.expect_http_error(400):
            browser.open(url, method='POST', data=json.dumps(data),
                         headers=self.api_headers)
