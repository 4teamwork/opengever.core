from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.response import IResponseContainer
from opengever.testing import IntegrationTestCase
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api


class TestTaskResponses(IntegrationTestCase):

    @browsing
    def test_response_and_response_changes_are_persistent(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.task)
        browser.click_on('task-transition-modify-deadline')
        browser.fill({'Response': u'Nicht mehr so dringend ...',
                      'New Deadline': '1.1.2017'})
        browser.click_on('Save')

        response = IResponseContainer(self.task).list()[-1]

        self.assertIsInstance(response, Persistent)
        self.assertIsInstance(response.changes, PersistentList)
        self.assertIsInstance(response.changes[0], PersistentMapping)


class TestTaskResponseForm(IntegrationTestCase):

    @browsing
    def test_shows_revoke_warn_message_only_on_final_transitions(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')

        self.assertEquals(
            ['This transtion revokes temporary permissions for the responsible '
             'user and agency group.'],
            info_messages())

        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-in-progress-resolved')

        self.assertEquals([], info_messages())

    @browsing
    def test_shows_no_revoke_warn_message_if_revoke_permissions_is_false(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.subtask.revoke_permissions = False
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')

        self.assertEquals(['Temporary permissions will not be revoked by this '
                           'transtion as revoke permissions is unchecked for '
                           'this task'],
                          info_messages())

    @browsing
    def test_redirects_to_task_if_user_has_access_rights(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.click_on('Save')

        self.assertEquals(['Review state successfully changed.'],
                          info_messages())
        self.assertEquals(self.subtask, browser.context)

    @browsing
    def test_redirects_to_portal_if_user_has_no_longer_access_rights(self, browser):
        self.login(self.administrator)

        self.set_workflow_state('task-state-open', self.task_in_protected_dossier)
        self.task_in_protected_dossier.task_type = 'information'
        self.task_in_protected_dossier.sync()

        self.login(self.regular_user, browser=browser)
        browser.open(self.task_in_protected_dossier, view='tabbedview_view-overview')
        browser.click_on('task-transition-open-tested-and-closed')
        browser.click_on('Save')

        self.assertEquals(
            ['Review state successfully changed, you are no longer permitted '
             'to access the task.'],
            info_messages())
        self.assertEquals(api.portal.get(), browser.context)
