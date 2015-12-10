from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.testing import FunctionalTestCase
from pyquery import PyQuery


class TestMeeting(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeeting, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.repo = create(Builder('repository_root'))
        self.repository_folder = create(Builder('repository')
                                        .within(self.repo))
        self.templates = create(Builder('templatedossier'))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repository_folder))
        self.sablon_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))
        self.container = create(Builder('committee_container').having(
                                protocol_template=self.sablon_template,
                                excerpt_template=self.sablon_template))
        self.committee = create(Builder('committee')
                                .within(self.container)
                                .link_with(self.repository_folder))
        self.committee_model = self.committee.load_model()
        self.peter = create(Builder('member')
                            .having(firstname=u'Peter', lastname=u'M\xfcller'))
        self.membership = create(Builder('membership')
                                 .having(committee=self.committee_model,
                                         member=self.peter)
                                 .as_active())

    def test_meeting_title(self):
        self.assertEqual(
            u'Bern, Oct 18, 2013',
            Meeting(location=u'Bern', start=self.localized_datetime(2013, 10, 18)).get_title())

        self.assertEqual(
            u'Oct 18, 2013',
            Meeting(start=self.localized_datetime(2013, 10, 18)).get_title())

    def test_meeting_link(self):
        meeting = create(Builder('meeting').having(
            committee=self.committee.load_model()))

        link = PyQuery(meeting.get_link())[0]

        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/view',
            link.get('href'))
        self.assertEqual('contenttype-opengever-meeting-meeting', link.get('class'))
        self.assertEqual(u'B\xe4rn, Dec 13, 2011', link.get('title'))
        self.assertEqual(u'B\xe4rn, Dec 13, 2011', link.text)

    @browsing
    def test_add_meeting_and_dossier(self, browser):
        # create meeting
        browser.login().open(self.committee, view='add-meeting')
        browser.fill({
            'Start': datetime(2010, 1, 1, 10),
            'End': datetime(2010, 1, 1, 11),
            'Location': 'Somewhere',
        }).submit()

        # create dossier
        self.assertEqual(u'Meeting on Jan 01, 2010',
                         browser.find('Title').value)
        browser.find('Save').click()

        # back to meeting page
        self.assertEqual(
            [u'The meeting and its dossier were created successfully'],
            info_messages())
        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/view',
            browser.url)

        committee_model = self.committee.load_model()
        self.assertEqual(1, len(committee_model.meetings))
        meeting = committee_model.meetings[0]

        self.assertEqual(self.localized_datetime(2010, 1, 1, 10), meeting.start)
        self.assertEqual(self.localized_datetime(2010, 1, 1, 11), meeting.end)
        self.assertEqual('Somewhere', meeting.location)
        self.assertEqual([Member.get(self.peter.member_id)],
                         meeting.participants)
        dossier = meeting.dossier_oguid.resolve_object()
        self.assertIsNotNone(dossier)
        self.assertEquals(u'Meeting on Jan 01, 2010', dossier.title)
        self.assertIsNotNone(meeting.modified)

    @browsing
    def test_close_meeting_generates_sequence_numbers_by_period(self, browser):
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model)
                         .link_with(self.meeting_dossier))
        create(Builder('agenda_item').having(meeting=meeting,
                                             title='Mach ize'))

        browser.login().open(meeting.get_url())
        browser.find('Close meeting').click()

        meeting = Meeting.query.get(meeting.meeting_id)
        self.assertEqual('closed', meeting.workflow_state)
        self.assertEqual(1, meeting.agenda_items[0].decision_number)
        self.assertEqual(1, meeting.meeting_number)
