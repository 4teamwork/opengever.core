from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.dossier.tests.test_dossier import TestDossier
from plone import api


class TestMeetingDossier(TestDossier):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeetingDossier, self).setUp()
        self.repo = create(Builder('repository_root'))
        self.repository_folder = create(Builder('repository')
                                        .within(self.repo))

    @browsing
    def test_add_meeting_menu_not_visible(self, browser):
        ttool = api.portal.get_tool('portal_types')
        browser.login().open(self.repository_folder)
        info = ttool.getTypeInfo('opengever.meeting.meetingdossier')
        self.assertEqual('Meeting Dossier', info.title)

        self.assertIsNone(browser.find(info.title))

    def test_factory_menu_sorting(self):
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
        self.grant('Contributor')
        self.assertItemsEqual(
            ['opengever.document.document',
             'ftw.mail.mail',
             'opengever.dossier.businesscasedossier',
             'opengever.meeting.proposal',
             'opengever.task.task'],
            [fti.id for fti in self.dossier.allowedContentTypes()])

    @browsing
    def test_tabbedview_tabs(self, browser):
        expected_tabs = ['Overview', 'Subdossiers', 'Documents', 'Tasks',
                         'Proposals', 'Participants', 'Trash', 'Journal',
                         'Info']

        browser.login().open(self.dossier, view='tabbed_view')
        self.assertEquals(expected_tabs, browser.css('li.formTab').text)
