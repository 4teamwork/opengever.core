from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.zipexport.zipfilestream import ZipFile
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Meeting
from opengever.meeting.model.generateddocument import GeneratedExcerpt
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import FunctionalTestCase
from StringIO import StringIO
import cgi
import transaction


class TestMeetingZipExportView(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeetingZipExportView, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier')
                              .within(self.repo_folder))

        self.meeting_dossier = create(Builder('meeting_dossier')
                                      .titled(u'Meeting Dossier')
                                      .within(self.repo_folder))

        self.sablon_template = create(
            Builder('sablontemplate')
            .with_asset_file('excerpt_template.docx'))

        container = create(
            Builder('committee_container')
            .having(agendaitem_list_template=self.sablon_template))

        self.committee = create(Builder('committee')
                                .having(protocol_template=self.sablon_template)
                                .within(container))

        self.hugo = create(Builder('member').having(firstname=u'h\xfcgo',
                                                    lastname="Boss",
                                                    email="boss@foo.ch"))

        self.sile = create(Builder('member').having(firstname="Silvia",
                                                    lastname="Pangani",
                                                    email="pangani@foo.ch"))

        self.peter = create(Builder('member').having(firstname="Peter",
                                                     lastname="Meter",
                                                     email="meter@foo.ch"))

        self.hans = create(Builder('member').having(firstname="Hans",
                                                    lastname="Besen"))

        self.roland = create(Builder('member').having(firstname="Roland",
                                                      lastname="Kuppler"))

        # set correct public url, used for generated meeting urls
        get_current_admin_unit().public_url = self.portal.absolute_url()
        transaction.commit()

    @browsing
    def test_zip_export_generate_protocol_if_there_is_none(self, browser):
        meeting = create(
            Builder('meeting')
            .having(committee=self.committee.load_model(),
                    start=self.localized_datetime(2013, 1, 1, 8, 30),
                    end=self.localized_datetime(2013, 1, 1, 10, 30),
                    location='There',
                    presidency=self.hugo,
                    participants=[self.peter,
                                  self.hans,
                                  self.roland],
                    secretary=self.sile)
            .link_with(self.meeting_dossier))

        browser.login().open(meeting.get_url(view='zipexport'))
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        meeting = Meeting.query.get(meeting.meeting_id)

        self.assertFalse(meeting.has_protocol_document())
        self.assertIn('Protocol-Community meeting.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_generated_protocol(self, browser):
        meeting = create(
            Builder('meeting')
            .having(committee=self.committee.load_model(),
                    start=self.localized_datetime(2013, 1, 1, 8, 30),
                    end=self.localized_datetime(2013, 1, 1, 10, 30),
                    location='There',
                    presidency=self.hugo,
                    participants=[self.peter,
                                  self.hans,
                                  self.roland],
                    secretary=self.sile)
            .link_with(self.meeting_dossier))

        # Add new protocol
        browser.login().visit(meeting.get_url())
        browser.css('a[href*="@@generate_protocol"]').first.click()
        browser.open(meeting.get_url(view='zipexport'))

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        meeting = Meeting.query.get(meeting.meeting_id)

        self.assertTrue(meeting.has_protocol_document())
        self.assertIn('Protocol-Community meeting.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_generate_protocol_if_outdated(self, browser):
        protocol = create(Builder('document')
                          .titled(u'Protocol')
                          .attach_file_containing(u"protocol",
                                                  u"protocol.docx")
                          .within(self.dossier))

        generated_protocol = create(Builder('generated_protocol')
                                    .for_document(protocol))

        meeting = create(
            Builder('meeting')
            .having(committee=self.committee.load_model(),
                    start=self.localized_datetime(2013, 1, 1, 8, 30),
                    end=self.localized_datetime(2013, 1, 1, 10, 30),
                    location='There',
                    presidency=self.hugo,
                    participants=[self.peter,
                                  self.hans,
                                  self.roland],
                    secretary=self.sile,
                    protocol_document=generated_protocol)
            .link_with(self.meeting_dossier))

        # CommitteeResponsible is assigned globally here for the sake of
        # simplicity
        self.grant('Contributor', 'Editor', 'Reader', 'MeetingUser',
                   'CommitteeResponsible')

        # Do a modification
        browser.login().open(meeting.get_url(view='protocol'))
        browser.fill({'Title': u'This is the modified different title than '
                               u'before'}).submit()
        browser.open(meeting.get_url(view='zipexport'))

        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertNotEquals(protocol.file.filename,
                             zip_file.filelist[0].filename)
        self.assertNotEquals(protocol.file.getSize(),
                             zip_file.filelist[0].file_size)
        self.assertIn('Protocol-This is the modified different title than'
                      ' before.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_agenda_items_attachments(self, browser):
        attachement1 = create(
            Builder('document')
            .titled(u'Attachem\xe4nt 1')
            .attach_file_containing(u"attachement",
                                    u"attachement1.docx")
            .within(self.dossier))

        attachement2 = create(
            Builder('document')
            .titled(u'Attachem\xe4nt 2')
            .attach_file_containing(u"attachement",
                                    u"attachement2.docx")
            .within(self.dossier))

        self.proposal_a = create(
            Builder('proposal')
            .titled(u'Proposal \xc4')
            .within(self.dossier)
            .as_submitted()
            .having(committee=self.committee.load_model())
            .relate_to(attachement1, attachement2))

        self.proposal_b = create(
            Builder('proposal')
            .titled(u'Proposal B')
            .within(self.dossier)
            .as_submitted()
            .having(committee=self.committee.load_model())
            .relate_to(attachement1))

        self.proposal_c = create(
            Builder('proposal')
            .titled(u'Proposal C')
            .within(self.dossier)
            .as_submitted()
            .having(committee=self.committee.load_model())
        )

        meeting = create(
            Builder('meeting')
            .having(committee=self.committee.load_model(),
                    start=self.localized_datetime(2013, 1, 1, 8, 30),
                    end=self.localized_datetime(2013, 1, 1, 10, 30),
                    location='There',
                    presidency=self.hugo,
                    participants=[self.peter,
                                  self.hans,
                                  self.roland],
                    secretary=self.sile)
            .scheduled_proposals([self.proposal_a, self.proposal_b])
            .link_with(self.meeting_dossier))

        browser.login().visit(meeting.get_url())
        browser.open(meeting.get_url(view='zipexport'))

        zip_file = ZipFile(StringIO(browser.contents), 'r')
        meeting = Meeting.query.get(meeting.meeting_id)

        self.assertIn('1. Proposal A/Attachemant 2.docx',
                      zip_file.namelist())
        self.assertIn('1. Proposal A/Attachemant 1.docx',
                      zip_file.namelist())
        self.assertIn('2. Proposal B/Attachemant 1.docx',
                      zip_file.namelist())
        self.assertNotIn('3. Proposal C',
                         zip_file.namelist())

    @browsing
    def test_zip_export_excerpt_is_not_exported(self, browser):
        excerpt = create(Builder('document')
                         .titled(u'Excerpt')
                         .attach_file_containing(u"excerpt",
                                                 u"excerpt.docx")
                         .within(self.dossier))

        generated_excerpt = create(Builder('generated_excerpt')
                                   .for_document(excerpt))
        # restore session by refreshing instance
        generated_excerpt = GeneratedExcerpt.get(generated_excerpt.document_id)

        meeting = create(
            Builder('meeting')
            .having(committee=self.committee.load_model(),
                    start=self.localized_datetime(2013, 1, 1, 8, 30),
                    end=self.localized_datetime(2013, 1, 1, 10, 30),
                    location='There',
                    presidency=self.hugo,
                    participants=[self.peter,
                                  self.hans,
                                  self.roland],
                    secretary=self.sile,
                    excerpt_documents=[generated_excerpt], )
            .link_with(self.meeting_dossier))

        browser.login().open(meeting.get_url(view='zipexport'))
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertNotIn('excerpt.docx', zip_file.namelist())

    @browsing
    def test_zip_export_agenda_items_list(self, browser):
        self.proposal_a = create(
            Builder('proposal')
            .titled(u'Proposal A')
            .within(self.dossier)
            .as_submitted()
            .having(committee=self.committee.load_model())
        )

        meeting = create(
            Builder('meeting')
            .having(committee=self.committee.load_model(),
                    start=self.localized_datetime(2013, 1, 1, 8, 30),
                    end=self.localized_datetime(2013, 1, 1, 10, 30),
                    location='There',
                    presidency=self.hugo,
                    participants=[self.peter,
                                  self.hans,
                                  self.roland],
                    secretary=self.sile)
            .scheduled_proposals([self.proposal_a, ])
            .link_with(self.meeting_dossier))

        browser.login().open(meeting.get_url(view='zipexport'))
        zip_file = ZipFile(StringIO(browser.contents), 'r')
        self.assertIn('Agendaitem list-Community meeting.docx',
                      zip_file.namelist())

    @browsing
    def test_zip_export_link_on_meeting_view(self, browser):
        meeting = create(
            Builder('meeting')
            .having(committee=self.committee.load_model(),
                    start=self.localized_datetime(2013, 1, 1, 8, 30),
                    end=self.localized_datetime(2013, 1, 1, 10, 30),
                    location='There',
                    presidency=self.hugo,
                    participants=[self.peter,
                                  self.hans,
                                  self.roland],
                    secretary=self.sile)
            .link_with(self.meeting_dossier))

        browser.login().open(meeting.get_url())
        self.assertTrue(browser.css('a.download-zipexport-btn'))
        self.assertEquals(
            'Export as Zip',
            browser.css('.item.zip-download > .title').first.text)

        browser.css('a.download-zipexport-btn').first.click()
        zip_file = ZipFile(StringIO(browser.contents), 'r')

        self.assertIsNone(zip_file.testzip(),
                          'Got a invalid zip file.')
        self.assertEquals(
            'Community meeting.zip',
            cgi.parse_header(browser.headers['content-disposition'])[1]['filename'],
            'Wrong zip filename.')
