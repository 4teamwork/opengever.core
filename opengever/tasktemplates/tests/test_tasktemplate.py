from datetime import date
from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_RESPONSIBLE_ID
from opengever.testing import SolrIntegrationTestCase
from plone import api


class TestTaskTemplates(SolrIntegrationTestCase):

    @browsing
    def test_adding_a_tasktemplate(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.tasktemplatefolder)
        factoriesmenu.add('Task Template')
        browser.fill(
            {'Title': 'Arbeitsplatz einrichten.',
             'Task type': 'comment',
             'Deadline in Days': u'10'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.dossier_responsible)
        form.find_widget('Issuer').fill(INTERACTIVE_ACTOR_RESPONSIBLE_ID)

        browser.click_on('Save')
        self.assertEquals(['Item created'], info_messages())

        tasktemplate = self.tasktemplatefolder.listFolderContents()[0]
        self.assertEquals(u'Arbeitsplatz einrichten.', tasktemplate.title)
        self.assertEquals(u'robert.ziegler', tasktemplate.responsible)
        self.assertEquals('fa', tasktemplate.responsible_client)
        self.assertEquals(INTERACTIVE_ACTOR_RESPONSIBLE_ID, tasktemplate.issuer)
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
    def test_view_displays_formatted_comments(self, browser):
        self.login(self.administrator, browser=browser)

        self.tasktemplate.text = (u'- T\xfcsteintrag' '\n'
                                  u'- m\xfet' '\n'
                                  u'- F\xfdrmat'
                                  '<script>alert("XSS!");</script>')

        browser.open(self.tasktemplate)

        # Get the cell of the comments
        cells = [row.css('td').first
                 for row in browser.css('.task-listing tr')
                 if len(row.css('th')) and row.css('th').first.text == 'Text']

        self.assertEquals(1, len(cells))

        self.assertEquals(u'- T\xfcsteintrag<br>'
                          u'- m\xfet<br>'
                          u'- F\xfdrmat'
                          u'&lt;script&gt;alert("XSS!");&lt;/script&gt;',
                          cells[0].normalized_innerHTML)

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
        factoriesmenu.add('Task Template')
        browser.fill(
            {'Title': 'Arbeitsplatz einrichten.',
             'Task type': 'comment',
             'Deadline in Days': u'10'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('team:1')
        form.find_widget('Issuer').fill(INTERACTIVE_ACTOR_RESPONSIBLE_ID)

        browser.click_on('Save')
        self.assertEquals(['Item created'], info_messages())

        tasktemplate = self.tasktemplatefolder.listFolderContents()[-1]
        self.assertEquals(u'Arbeitsplatz einrichten.', tasktemplate.title)
        self.assertEquals(u'team:1', tasktemplate.responsible)
        self.assertEquals('fa', tasktemplate.responsible_client)
        self.assertEquals(INTERACTIVE_ACTOR_RESPONSIBLE_ID, tasktemplate.issuer)
        self.assertEquals(10, tasktemplate.deadline)

    @browsing
    def test_interactive_actors_can_be_selected_as_responsible_and_issuer(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.tasktemplatefolder)
        factoriesmenu.add('Task Template')
        browser.fill(
            {'Title': 'Arbeitsplatz einrichten.',
             'Task type': 'comment',
             'Deadline in Days': u'10'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(INTERACTIVE_ACTOR_RESPONSIBLE_ID)
        form.find_widget('Issuer').fill(INTERACTIVE_ACTOR_RESPONSIBLE_ID)

        browser.click_on('Save')
        self.assertEquals(['Item created'], info_messages())

        tasktemplate = self.tasktemplatefolder.listFolderContents()[-1]

        self.assertIsNone(tasktemplate.responsible_client)
        self.assertEquals('interactive_actor:responsible', tasktemplate.responsible)
        self.assertEquals('interactive_actor:responsible', tasktemplate.issuer)

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
            ['Items deleted successfully.'], info_messages())
        self.assertEquals([], self.tasktemplatefolder.listFolderContents())

    @browsing
    def test_responsible_is_not_required(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.tasktemplatefolder)
        factoriesmenu.add('Task Template')
        browser.fill(
            {'Title': 'Arbeitsplatz einrichten.',
             'Task type': 'comment',
             'Deadline in Days': u'10'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Issuer').fill(INTERACTIVE_ACTOR_RESPONSIBLE_ID)

        browser.click_on('Save')
        self.assertEquals(['Item created'], info_messages())
        tasktemplate = self.tasktemplatefolder.listFolderContents()[-1]
        self.assertEquals(u'Arbeitsplatz einrichten.', tasktemplate.title)
        self.assertEquals(None, tasktemplate.responsible)

    @browsing
    def test_view_displays_deadline(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.tasktemplate)

        # Get the cells in the column "deadline".
        cells = [row.css('td').first
                 for row in browser.css('.task-listing tr')
                 if len(row.css('th')) and row.css('th').first.text == 'Deadline in Days']

        self.assertEquals(
            ["10"],
            [cell.text for cell in cells]
        )

    def test_get_absolute_deadline_returns_the_resolved_deadline(self):
        self.login(self.administrator)

        self.tasktemplate.deadline = 5

        with freeze(datetime(2021, 12, 10)):
            self.assertEqual(date(2021, 12, 15), self.tasktemplate.get_absolute_deadline())
