from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.model.generateddocument import GeneratedExcerpt
from opengever.meeting.model.meeting import Meeting
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import FunctionalTestCase
import transaction


class TestMeetingView(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeetingView, self).setUp()

        self.repository_root = create(Builder('repository_root'))
        self.dossier = create(Builder('dossier')
                              .within(self.repository_root))

        self.attachement = create(Builder('document')
                                  .attach_file_containing(u"attachement",
                                                          u"attachement.docx")
                                  .within(self.dossier))

        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))

        self.sablon_template = create(
            Builder('sablontemplate')
            .with_asset_file('excerpt_template.docx'))

        self.preprotocol = create(Builder('document')
                                  .attach_file_containing(u"preprotocol",
                                                          u"preprotocol.docx")
                                  .within(self.dossier))

        self.protocol = create(Builder('document')
                               .attach_file_containing(u"protocol",
                                                       u"protocol.docx")
                               .within(self.dossier))

        self.excerpt = create(Builder('document')
                              .attach_file_containing(u"excerpt",
                                                      u"excerpt.docx")
                              .within(self.dossier))

        self.generated_excerpt = create(Builder('generated_excerpt')
                                        .for_document(self.excerpt))

        self.hugo = create(Builder('member').having(firstname=u'h\xfcgo',
                                                    lastname="Boss"))

        self.sile = create(Builder('member').having(firstname="Silvia",
                                                    lastname="Pangani"))

        self.peter = create(Builder('member').having(firstname="Peter",
                                                     lastname="Meter"))

        self.hans = create(Builder('member').having(firstname="Hans",
                                                    lastname="Besen"))

        self.roland = create(Builder('member').having(firstname="Roland",
                                                      lastname="Kuppler"))

        self.proposal_a = create(Builder('proposal')
                                 .titled(u'Proposal A')
                                 .within(self.dossier)
                                 .as_submitted()
                                 .having(committee=self.committee.load_model(),
                                         submitted_excerpt_document=self.generated_excerpt,)
                                 .relate_to(self.attachement))

        self.proposal_b = create(Builder('proposal')
                                 .titled(u'Proposal B')
                                 .within(self.dossier)
                                 .as_submitted()
                                 .having(committee=self.committee.load_model()))

        self.generated_protocol = create(Builder('generated_protocol')
                                         .for_document(self.protocol))

        self.generated_preprotocol = create(Builder('generated_preprotocol')
                                            .for_document(self.preprotocol))

        # restore session by refreshing instance
        self.generated_excerpt = GeneratedExcerpt.get(self.generated_excerpt.document_id)

        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model(),
                                      start=datetime(2013, 1, 1, 8, 30),
                                      end=datetime(2013, 1, 1, 10, 30),
                                      location='There',
                                      presidency=self.hugo,
                                      participants = [self.peter,
                                                      self.hans,
                                                      self.roland],
                                      secretary=self.sile,
                                      pre_protocol_document=self.generated_preprotocol,
                                      protocol_document=self.generated_protocol,
                                      excerpt_documents=[self.generated_excerpt],)
                              .scheduled_proposals([self.proposal_a, self.proposal_b]))

        # set correct public url, used for generated meeting urls
        get_current_admin_unit().public_url = self.portal.absolute_url()
        transaction.commit()

    @browsing
    def test_participants_listing_precidency_is_existing(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals([u'h\xfcgo Boss'], browser.css("#meeting_presidency").text)

    @browsing
    def test_participants_listing_no_precidency_must_not_raise(self, browser):
        Meeting.query.all()[0].presidency = None
        transaction.commit()
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals([''], browser.css("#meeting_presidency").text)

    @browsing
    def test_participants_listing_secretary_is_existing(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals(['Silvia Pangani'], browser.css("#meeting_secretary").text)

    @browsing
    def test_participants_listing_no_secretary_must_not_raise(self, browser):
        Meeting.query.all()[0].secretary = None
        transaction.commit()
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals([''], browser.css("#meeting_secretary").text)

    @browsing
    def test_participants_listing_participants_is_existing(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals(['Peter Meter Hans Besen Roland Kuppler'],
                          browser.css("#meeting_participants").text)

    @browsing
    def test_participants_listing_empty_participants_must_not_raise(self, browser):
        Meeting.query.all()[0].participants = []
        transaction.commit()
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals([''], browser.css("#meeting_participants").text)

    @browsing
    def test_metadata_starttime_is_existing(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('08:30 AM', browser.css("#meeting_time span")[0].text)

    @browsing
    def test_metadata_endtime_is_existing(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('10:30 AM', browser.css("#meeting_time span")[1].text)

    @browsing
    def test_metadata_no_endtime_must_not_raise(self, browser):
        Meeting.query.all()[0].end = None
        transaction.commit()
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('', browser.css("#meeting_time span")[1].text)

    @browsing
    def test_metadata_state_pending_exists(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('Pending', browser.css(".state").first.text)

    @browsing
    def test_generated_preprotocol_exists(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('preprotocol', browser.css(".protocol > a")[0].text)
        self.assertEquals(self.preprotocol.absolute_url(), browser.css(".protocol > a")[0].get('href'))

    @browsing
    def test_generated_protocol_exists(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('protocol', browser.css(".protocol > a")[1].text)
        self.assertEquals(self.protocol.absolute_url(), browser.css(".protocol > a")[1].get('href'))

    @browsing
    def test_generated_exceprts_exists(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('excerpt', browser.css(".excerpts a").first.text)
        self.assertEquals(self.excerpt.absolute_url(), browser.css(".excerpts a").first.get('href'))

    @browsing
    def test_generated_proposal_exceprt_exists(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('excerpt', browser.css(".summary > a").first.text)
        self.assertEquals(self.excerpt.absolute_url(), browser.css(".summary > a").first.get('href'))

    @browsing
    def test_proposal_attachement_exists(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('attachement', browser.css(".attachements a").first.text)

    @browsing
    def test_proposal_attachement_link_exists(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals(
            self.proposal_a.load_model().resolve_submitted_documents()[0].absolute_url(),
            browser.css(".attachements a").first.get('href'))

    @browsing
    def test_proposal_is_expandable(self, browser):
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        self.assertEquals('expandable',
                          browser.css("#agenda_items tr")[0].get('class'))

        self.assertEquals('', browser.css("#agenda_items tr")[1].get('class'))
