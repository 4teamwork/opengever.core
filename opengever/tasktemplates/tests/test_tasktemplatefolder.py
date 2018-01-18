from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import IntegrationTestCase
from plone import api


class TestTaskTemplateFolder(IntegrationTestCase):

    @browsing
    def test_adding(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.templates)
        factoriesmenu.add(u'TaskTemplateFolder')
        browser.fill({'Title': 'Baugesuch'}).submit()

        self.assertEquals(['Item created'], info_messages())
        self.assertEquals(['Baugesuch'], browser.css('h1').text)
        self.assertEquals('opengever.tasktemplates.tasktemplatefolder',
                          browser.context.portal_type)

    def test_default_state_is_inactive(self):
        self.login(self.administrator)
        tasktemplatefolder = create(Builder('tasktemplatefolder')
                                    .titled(u'Verfahren Neuanstellung')
                                    .within(self.templates))

        self.assertEquals('tasktemplatefolder-state-inactiv',
                          api.content.get_state(tasktemplatefolder))

