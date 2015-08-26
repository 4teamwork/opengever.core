from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.testing import FunctionalTestCase
from plone import api


class TestMeetingDossier(FunctionalTestCase):

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
