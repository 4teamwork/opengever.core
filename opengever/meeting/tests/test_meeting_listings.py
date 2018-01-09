from AccessControl import Unauthorized
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import localized_datetime
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
            'vertrage-und-vereinbarungen/dossier-7" '
            'title="Sitzungsdossier 9/2017" '
            'class="contenttype-opengever-meeting-meetingdossier"'
            '>Sitzungsdossier 9/2017</a>',
            result)

    @browsing
    def test_entries_are_sorted_by_date(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.committee, view='tabbedview_view-meetings')
        self.assertEquals(
            ['Jul 17, 2015', 'Jul 17, 2016', 'Sep 12, 2016'],
            browser.css('#listing_container tbody tr td:nth-child(4)').text)

        self.login(self.committee_responsible)
        create(Builder('meeting')
               .having(committee=self.committee,
                       start=localized_datetime(2016, 8, 21)))

        self.login(self.meeting_user, browser)
        browser.open(self.committee, view='tabbedview_view-meetings')
        self.assertEquals(
            ['Jul 17, 2015', 'Jul 17, 2016', 'Aug 21, 2016', 'Sep 12, 2016'],
            browser.css('#listing_container tbody tr td:nth-child(4)').text)
