from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.toc.alphabetical import AlphabeticalToc
from opengever.testing import FunctionalTestCase
import pytz


class TestTOC(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER
    maxDiff = None

    def setUp(self):
        super(TestTOC, self).setUp()

        self.committee = create(Builder('committee_model'))
        self.meeting1 = create(Builder('meeting').having(
            committee=self.committee,
            start=pytz.UTC.localize(datetime(2010, 1, 1, 10, 30)),
            protocol_start_page_number=33))
        self.meeting2 = create(Builder('meeting').having(
            committee=self.committee,
            start=pytz.UTC.localize(datetime(2010, 12, 31, 18, 30)),
            protocol_start_page_number=129))

        proposal1_1 = create(Builder('proposal_model').having(
            title=u'Proposal 1',
            repository_folder_title='Business',
            dossier_reference_number='1.1.4 / 1',
            int_id=1))
        proposal1_2 = create(Builder('proposal_model').having(
            title=u'\xdchhh',
            repository_folder_title='Business',
            dossier_reference_number='1.1.4 / 2',
            int_id=2))

        proposal2_1 = create(Builder('proposal_model').having(
            title=u'Proposal 3',
            repository_folder_title='Stuff',
            dossier_reference_number='2.1.4 / 1',
            int_id=3))
        proposal2_2 = create(Builder('proposal_model').having(
            title=u'Anything goes',
            repository_folder_title='Other Stuff',
            dossier_reference_number='3.1.4 / 77',
            int_id=4))

        create(Builder('agenda_item').having(
            meeting=self.meeting1,
            proposal=proposal1_1,
            decision_number=2,
            ))
        create(Builder('agenda_item').having(
            meeting=self.meeting1,
            proposal=proposal1_2,
            decision_number=3,
            ))
        create(Builder('agenda_item').having(
            meeting=self.meeting2,
            proposal=proposal2_1,
            decision_number=4,
            ))
        create(Builder('agenda_item').having(
            meeting=self.meeting2,
            proposal=proposal2_2,
            decision_number=5,
            ))

        self.period = create(Builder('period').having(
            date_from=date(2010, 1, 1),
            date_to=date(2010, 12, 31),
            committee=self.committee))

    def test_toc(self):
        expected = {'toc': [{
            'group_title': u'5',
            'contents': [
                {
                    'title': u'5 Dinge',
                    'dossier_reference_number': '1.1.4 / 2',
                    'repository_folder_title': 'Business',
                    'meeting_date': u'Jan 01, 2010',
                    'decision_number': 3,
                    'has_proposal': True,
                    'meeting_start_page_number': 33,
                }]
            }, {
            'group_title': u'A',
            'contents': [
                {
                    'title': u'Anything goes',
                    'dossier_reference_number': '3.1.4 / 77',
                    'repository_folder_title': 'Other Stuff',
                    'meeting_date': u'Dec 31, 2010',
                    'decision_number': 5,
                    'has_proposal': True,
                    'meeting_start_page_number': 129,
                }]
            }, {
            'group_title': u'P',
            'contents': [{
                'title': u'Proposal 1',
                'dossier_reference_number': u'1.1.4 / 1',
                'repository_folder_title': u'Business',
                'meeting_date': 'Jan 01, 2010',
                'decision_number': 2,
                'has_proposal': True,
                'meeting_start_page_number': 33,

            }, {
                'title': u'Proposal 3',
                'dossier_reference_number': '2.1.4 / 1',
                'repository_folder_title': 'Stuff',
                'meeting_date': u'Dec 31, 2010',
                'decision_number': 4,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }]}
        self.assertEqual(expected, AlphabeticalToc(self.period).get_json())

    @browsing
    def test_shows_statusmessage_when_no_template_is_configured(self, browser):
        container = create(Builder('committee_container'))
        committee = create(Builder('committee')
                           .within(container))
        period = create(Builder('period').having(
            date_from=date(2010, 1, 1),
            date_to=date(2010, 12, 31),
            committee=committee.load_model()))

        url = period.get_url(committee)
        browser.login().open(url, view='alphabetical_toc')
        self.assertEqual(u'There is no toc template configured, toc could '
                         'not be generated.',
                         error_messages()[0])

    @browsing
    def test_toc_can_be_downloaded(self, browser):
        self.templates = create(Builder('templatedossier'))
        self.sablon_template = create(Builder('sablontemplate')
                                      .within(self.templates)
                                      .with_asset_file('sablon_template.docx'))
        container = create(Builder('committee_container'))
        committee = create(Builder('committee')
                           .having(toc_template=self.sablon_template)
                           .within(container))
        create(Builder('period').having(
            date_from=date(2010, 1, 1),
            date_to=date(2010, 12, 31),
            committee=committee.load_model()))

        browser.login().open(committee, view='tabbedview_view-periods')
        browser.find('Alphabetical').click()

        self.assertDictContainsSubset(
            {'status': '200 Ok',
             'content-disposition': 'attachment; filename="Alphabetical Toc.docx"',
             'x-frame-options': 'SAMEORIGIN',
             'content-type': MIME_DOCX,
             'x-theme-disabled': 'True'},
            browser.headers)
        self.assertIsNotNone(browser.contents)
