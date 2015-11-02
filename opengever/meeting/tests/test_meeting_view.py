from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model.generateddocument import GeneratedExcerpt
from opengever.meeting.model.meeting import Meeting
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import FunctionalTestCase
import transaction


class TestMeetingView(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeetingView, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.repository_root = create(Builder('repository_root'))
        self.dossier = create(Builder('dossier')
                              .within(self.repository_root))

        self.meeting_dossier = create(Builder('meeting_dossier')
                                      .titled(u'Meeting Dossier')
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

        self.protocol = create(Builder('document')
                               .titled(u'Protocol')
                               .attach_file_containing(u"protocol",
                                                       u"protocol.docx")
                               .within(self.dossier))

        self.excerpt = create(Builder('document')
                              .titled(u'Excerpt')
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

        # restore session by refreshing instance
        self.generated_excerpt = GeneratedExcerpt.get(self.generated_excerpt.document_id)

        self.meeting = create(
            Builder('meeting')
            .having(committee=self.committee.load_model(),
                    start=datetime(2013, 1, 1, 8, 30),
                    end=datetime(2013, 1, 1, 10, 30),
                    location='There',
                    presidency=self.hugo,
                    participants=[self.peter,
                                  self.hans,
                                  self.roland],
                    secretary=self.sile,
                    protocol_document=self.generated_protocol,
                    excerpt_documents=[self.generated_excerpt],)
            .scheduled_proposals([self.proposal_a, self.proposal_b])
            .link_with(self.meeting_dossier))

        # set correct public url, used for generated meeting urls
        get_current_admin_unit().public_url = self.portal.absolute_url()
        transaction.commit()

    @browsing
    def test_meeting_dossier_is_linked_from_meeting_view(self, browser):
        browser.login().open(self.meeting.get_url())

        link_node = browser.css('#related_dossier + dd > a').first
        self.assertEqual('Meeting Dossier', link_node.text)
        self.assertEqual(self.meeting_dossier.absolute_url(),
                         link_node.get('href'))

    @browsing
    def test_accessing_the_meeting_directly_shows_meeting_view(self, browser):
        browser.login().open(self.meeting.get_url(view=None))

        self.assertEquals(['There, Jan 01, 2013'], browser.css('h1').text)

    @browsing
    def test_participants_listing_precidency_is_existing(self, browser):
        browser.login().open(self.meeting.get_url())
        self.assertEquals([u'h\xfcgo Boss'], browser.css("#meeting_presidency + dd").text)

    @browsing
    def test_participants_listing_no_precidency_must_not_raise(self, browser):
        Meeting.query.all()[0].presidency = None
        transaction.commit()
        browser.login().open(self.meeting.get_url())
        self.assertEquals([], browser.css("#meeting_presidency + dd").text)

    @browsing
    def test_participants_listing_secretary_is_existing(self, browser):
        browser.login().open(self.meeting.get_url())
        self.assertEquals(['Silvia Pangani'], browser.css("#meeting_secretary + dd").text)

    @browsing
    def test_participants_listing_no_secretary_must_not_raise(self, browser):
        Meeting.query.all()[0].secretary = None
        transaction.commit()
        browser.login().open(self.meeting.get_url())
        self.assertEquals([], browser.css("#meeting_secretary + dd").text)

    @browsing
    def test_participants_listing_participants_is_existing(self, browser):
        browser.login().open(self.meeting.get_url())
        self.assertEquals(['Peter Meter Hans Besen Roland Kuppler'],
                          browser.css("#meeting_participants + dd").text)

    @browsing
    def test_participants_listing_empty_participants_must_not_raise(self, browser):
        Meeting.query.all()[0].participants = []
        transaction.commit()
        browser.login().open(self.meeting.get_url())
        self.assertEquals([''], browser.css("#meeting_participants + dd").text)

    @browsing
    def test_metadata_starttime_is_existing(self, browser):
        browser.login().open(self.meeting.get_url())
        self.assertEquals('08:30 AM - 10:30 AM', browser.css("#meeting_time + dd").first.text)

    @browsing
    def test_metadata_no_endtime_must_not_raise(self, browser):
        Meeting.query.all()[0].end = None
        transaction.commit()
        browser.login().open(self.meeting.get_url())
        self.assertEquals('08:30 AM -', browser.css("#meeting_time + dd").first.text)

    @browsing
    def test_metadata_state_pending_exists(self, browser):
        browser.login().open(self.meeting.get_url())
        self.assertEquals('pending', browser.css(".workflow_state + dd").first.text)

    @browsing
    def test_generated_protocol_exists(self, browser):
        browser.login().open(self.meeting.get_url())
        self.assertEquals('Protocol', browser.css(".protocol > a").first.text)
        self.assertEquals(self.protocol.absolute_url(), browser.css(".protocol > a").first.get('href'))

    @browsing
    def test_generated_exceprts_exists(self, browser):
        browser.login().open(self.meeting.get_url())
        self.assertEquals('Excerpt', browser.css(".excerpts a").first.text)
        self.assertEquals(self.excerpt.absolute_url(), browser.css(".excerpts a").first.get('href'))
