from ftw.contentmenu.menu import FactoriesMenu
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api


class TestMeetingDossier(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_add_meeting_menu_not_visible(self, browser):
        self.login(self.dossier_responsible, browser)

        ttool = api.portal.get_tool('portal_types')
        browser.open(self.leaf_repofolder)
        info = ttool.getTypeInfo('opengever.meeting.meetingdossier')
        self.assertEqual('Meeting Dossier', info.title)

        self.assertIsNone(browser.find(info.title))

    def test_factory_menu_sorting(self):
        self.login(self.dossier_responsible)

        menu = FactoriesMenu(self.dossier)
        menu_items = menu.getMenuItems(self.dossier, self.dossier.REQUEST)

        self.assertEquals(
            [u'Document',
             'document_with_template',
             u'Task',
             'Add task from template',
             u'Subdossier',
             u'Participant',
             u'Proposal'],
            [item.get('title') for item in menu_items])

    def test_default_addable_types(self):
        self.login(self.dossier_responsible)
        self.assertItemsEqual(
            ['opengever.document.document',
             'ftw.mail.mail',
             'opengever.dossier.businesscasedossier',
             'opengever.meeting.proposal',
             'opengever.task.task'],
            [fti.id for fti in self.dossier.allowedContentTypes()])

    @browsing
    def test_tabbedview_tabs(self, browser):
        self.login(self.dossier_responsible, browser)
        expected_tabs = ['Overview', 'Subdossiers', 'Documents', 'Tasks',
                         'Proposals', 'Participants', 'Trash', 'Journal',
                         'Info']

        browser.open(self.dossier, view='tabbed_view')
        self.assertEquals(expected_tabs, browser.css('li.formTab').text)

    @browsing
    def test_title_field_hidden_in_meeting_dossier_add_form(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.leaf_repofolder,
                     view='++add++opengever.meeting.meetingdossier')

        self.assertIsNotNone(
            browser.css('[name="form.widgets.IOpenGeverBase.title"]'),
            'Hidden title field not found.')
        self.assertIsNone(
            browser.find('Title'), 'Title field is unexpectedly visible.')

    @browsing
    def test_title_field_hidden_in_meeting_dossier_edit_form(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.meeting_dossier, view='@@edit')

        self.assertIsNotNone(
            browser.css('[name="form.widgets.IOpenGeverBase.title"]'),
            'Hidden title field not found.')
        self.assertIsNone(
            browser.find('Title'), 'Title field is unexpectedly visible.')
