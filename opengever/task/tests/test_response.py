from ftw.testbrowser import browsing
from opengever.task.adapters import IResponseContainer
from opengever.testing import IntegrationTestCase
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping


class TestTaskResponses(IntegrationTestCase):

    @browsing
    def test_response_and_response_changes_are_persistent(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.task)
        browser.click_on('task-transition-modify-deadline')
        browser.fill({'Response': u'Nicht mehr so dringend ...',
                      'New Deadline': '1.1.2017'})
        browser.click_on('Save')

        response = IResponseContainer(self.task)[-1]

        self.assertIsInstance(response, Persistent)
        self.assertIsInstance(response.changes, PersistentList)
        self.assertIsInstance(response.changes[0], PersistentMapping)
