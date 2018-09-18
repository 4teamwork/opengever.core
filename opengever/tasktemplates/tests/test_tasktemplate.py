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

    @browsing
    def test_teams_can_be_selected_as_responsible(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.tasktemplatefolder)
        factoriesmenu.add('TaskTemplate')
        browser.fill(
            {'Title': 'Arbeitsplatz einrichten.',
             'Task Type': 'comment',
             'Deadline in Days': u'10'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('team:1')
        form.find_widget('Issuer').fill(u'responsible')

        browser.click_on('Save')
        self.assertEquals(['Item created'], info_messages())

        tasktemplate = self.tasktemplatefolder.listFolderContents()[-1]
        self.assertEquals(u'Arbeitsplatz einrichten.', tasktemplate.title)
        self.assertEquals(u'team:1', tasktemplate.responsible)
        self.assertEquals('fa', tasktemplate.responsible_client)
        self.assertEquals(u'responsible', tasktemplate.issuer)
        self.assertEquals(10, tasktemplate.deadline)

    @browsing
    def test_deleting_a_tasktemplatefolder_is_possible(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        title = self.tasktemplatefolder.title
        self.assertIn(title, [template.title for template in
                              self.templates.listFolderContents()])

        browser.open(self.tasktemplatefolder)
        self.assertIn(
            'Delete',
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)

        browser.click_on('Delete')
        browser.click_on('Delete')

        self.assertEquals(['Verfahren Neuanstellung has been deleted.'], info_messages())
        self.assertNotIn(title, [template.title for template in
                                 self.templates.listFolderContents()])

    @browsing
    def test_deleting_a_tasktemplate_is_possible(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        title = self.tasktemplate.title
        self.assertIn(title, [template.title for template in
                              self.tasktemplatefolder.listFolderContents()])

        browser.open(self.tasktemplate)
        self.assertIn(
            'Delete',
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)

        browser.click_on('Delete')
        browser.click_on('Delete')

        self.assertEquals(['Arbeitsplatz einrichten. has been deleted.'], info_messages())
        self.assertNotIn(title, [template.title for template in
                                 self.tasktemplatefolder.listFolderContents()])

    @browsing
    def test_deleting_tasktemplates_is_possible(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.tasktemplatefolder, view="tabbed_view/listing?view_name=tasktemplates")

        self.assertIn(
            'Delete',
            browser.css('#tabbedview-menu .tabbedview-action-list a').text)

        data = self.make_path_param(self.tasktemplate)
        browser.open(self.tasktemplatefolder, data,
                     view='folder_delete_confirmation')
        browser.click_on('Delete')

        self.assertEquals(
            ['Items successfully deleted.'], info_messages())
        self.assertEquals([], self.tasktemplatefolder.listFolderContents())
