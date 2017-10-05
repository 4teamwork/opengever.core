from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import IntegrationTestCase
from plone import api


class TestTaskTemplates(IntegrationTestCase):

    @browsing
    def test_adding_a_tasktemplate(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.tasktemplatefolder)
        factoriesmenu.add('TaskTemplate')
        browser.fill(
            {'Title': 'Arbeitsplatz einrichten.',
             'Task Type': 'comment',
             'Deadline in Days': u'10'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('fa:robert.ziegler')
        form.find_widget('Issuer').fill(u'responsible')

        browser.click_on('Save')
        self.assertEquals(['Item created'], info_messages())

        tasktemplate = self.tasktemplatefolder.listFolderContents()[0]
        self.assertEquals(u'Arbeitsplatz einrichten.', tasktemplate.title)
        self.assertEquals(u'robert.ziegler', tasktemplate.responsible)
        self.assertEquals('fa', tasktemplate.responsible_client)
        self.assertEquals(u'responsible', tasktemplate.issuer)
        self.assertEquals(10, tasktemplate.deadline)

    def test_tasktemplate_is_in_active_state_per_default(self):
        self.login(self.administrator)

        self.assertEquals('tasktemplate-state-active',
                          api.content.get_state(self.tasktemplate))

    @browsing
    def test_view(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.tasktemplate)
        self.assertEquals(['Arbeitsplatz einrichten.'],
                          browser.css('.documentFirstHeading').text)

    @browsing
    def test_tasktemplatefolder_can_be_edited_when_activated(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.tasktemplatefolder, view='@@edit')
        browser.fill({'Title': 'Arbeitsplatz inkl. PC einrichten'})
        browser.find_button_by_label('Save').click()

        self.assertEquals(self.tasktemplatefolder.absolute_url(), browser.url)
        self.assertEquals(u'Arbeitsplatz inkl. PC einrichten',
                          self.tasktemplatefolder.title)
