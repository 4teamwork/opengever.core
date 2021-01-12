from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.testing import IntegrationTestCase
from plone import api
from zope.interface import alsoProvides


class TestWorfklowForTasksFromTemplatefolders(IntegrationTestCase):

    @browsing
    def test_cancel(self, browser):
        self.login(self.regular_user, browser=browser)

        alsoProvides(self.task, IFromSequentialTasktemplate)
        self.set_workflow_state('task-state-in-progress', self.task)
        self.set_workflow_state('task-state-in-progress', self.subtask)


        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Cancel')
        browser.fill({'Response': u'Projekt wurde gestoppt.'})
        browser.click_on('Save')

        self.assertEquals(
            'task-state-cancelled', api.content.get_state(self.task))
        self.assertEquals(
            'task-state-cancelled', api.content.get_state(self.subtask))
