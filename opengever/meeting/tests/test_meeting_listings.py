from AccessControl import Unauthorized
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.meeting.tabs.meetinglisting import dossier_link_or_title


class TestMeetingListing(IntegrationTestCase):
    features = ('meeting',)

    maxDiff = None

    @browsing
    def test_span_appears_if_no_view_permission_on_dossier(self, browser):
        self.login(self.dossier_responsible, browser)

        self.meeting_dossier.__ac_local_roles_block__ = True
        self.meeting_dossier.reindexObjectSecurity()

        self.login(self.meeting_user, browser)
        with self.assertRaises(Unauthorized):
            self.meeting_dossier

        result = dossier_link_or_title(self.meeting.model, None)

        self.assertEquals(
            '<span title="Sitzungsdossier 9/2017" '
            'class="contenttype-opengever-meeting-meetingdossier">'
            'Sitzungsdossier 9/2017</span>',
            result)

    @browsing
    def test_link_appears_if_view_permission_on_dossier(self, browser):
        self.login(self.meeting_user, browser)
        result = dossier_link_or_title(self.meeting.model, None)

        self.assertEquals(
            '<a href="http://nohost/plone/ordnungssystem/fuhrung/'
            'vertrage-und-vereinbarungen/dossier-6" '
            'title="Sitzungsdossier 9/2017" '
            'class="contenttype-opengever-meeting-meetingdossier"'
            '>Sitzungsdossier 9/2017</a>',
            result)
