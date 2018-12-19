from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import InsufficientPrivileges
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testing import freeze
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.toc.alphabetical import AlphabeticalToc
from opengever.meeting.toc.repository import RepositoryBasedTOC
from opengever.testing import FunctionalTestCase
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import pytz
import transaction


class TestAlphabeticalTOC(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER
    maxDiff = None

    expected_toc_json = {'toc': [{
        'group_title': u'A',
        'contents': [
            {
                'title': u'Anything goes',
                'dossier_reference_number': '3.1.4 / 77',
                'repository_folder_title': 'Other Stuff',
                'meeting_date': u'31.12.2010',
                'decision_number': 5,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }, {
        'group_title': u'N',
        'contents': [
            {
                'title': u'Nahhh not here either',
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 7,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }, {
                'title': u'No Proposal here',
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 6,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }]
        }, {
        'group_title': u'P',
        'contents': [
            {
                'title': u'proposal 1',
                'dossier_reference_number': u'1.1.4 / 1',
                'repository_folder_title': u'Business',
                'meeting_date': '01.01.2010',
                'decision_number': 2,
                'has_proposal': True,
                'meeting_start_page_number': 33,
                }, {
                'title': u'Proposal 3',
                'dossier_reference_number': '2.1.4 / 1',
                'repository_folder_title': 'Stuff',
                'meeting_date': u'31.12.2010',
                'decision_number': 4,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }, {
        'group_title': u'\xdc',
        'contents': [
            {
                'title': u'\xdchhh',
                'dossier_reference_number': '1.1.4 / 2',
                'repository_folder_title': 'Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 3,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }]
        }]
    }

    def setUp(self):
        super(TestAlphabeticalTOC, self).setUp()
        self.container = create(Builder('committee_container'))

        # freeze date to make sure the default period is 2016
        with freeze(datetime(2016, 12, 3)):
            self.committee = create(Builder('committee')
                                    .within(self.container))
        self.committee_model = self.committee.load_model()
        self.period = create(Builder('period').having(
            title=u'2010',
            date_from=date(2010, 1, 1),
            date_to=date(2010, 12, 31),
            committee=self.committee_model))

        self.meeting_before = create(Builder('meeting').having(
            committee=self.committee_model,
            start=pytz.UTC.localize(datetime(2009, 12, 31, 23, 45)),
            protocol_start_page_number=99))

        self.meeting1 = create(Builder('meeting').having(
            committee=self.committee_model,
            start=pytz.UTC.localize(datetime(2010, 1, 1, 10, 30)),
            protocol_start_page_number=33))
        self.meeting2 = create(Builder('meeting').having(
            committee=self.committee_model,
            start=pytz.UTC.localize(datetime(2010, 12, 31, 18, 30)),
            protocol_start_page_number=129))

        self.meeting_after = create(Builder('meeting').having(
            committee=self.committee_model,
            start=pytz.UTC.localize(datetime(2011, 1, 1, 0, 0)),
            protocol_start_page_number=99))

        proposal1_1 = create(Builder('submitted_proposal').having(
            title=u'proposal 1',
            repository_folder_title='Business',
            dossier_reference_number='1.1.4 / 1',
            int_id=1).within(self.committee))
        proposal1_2 = create(Builder('submitted_proposal').having(
            title=u'\xdchhh',
            repository_folder_title='Business',
            dossier_reference_number='1.1.4 / 2',
            int_id=2).within(self.committee))

        proposal2_1 = create(Builder('submitted_proposal').having(
            title=u'Proposal 3',
            repository_folder_title='Stuff',
            dossier_reference_number='2.1.4 / 1',
            int_id=3).within(self.committee))
        proposal2_2 = create(Builder('submitted_proposal').having(
            title=u'Anything goes',
            repository_folder_title='Other Stuff',
            dossier_reference_number='3.1.4 / 77',
            int_id=4).within(self.committee))

        create(Builder('agenda_item').having(
            meeting=self.meeting_before,
            title=u'I am before period start',
            decision_number=1,
        ))

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
        create(Builder('agenda_item').having(
            meeting=self.meeting2,
            title=u'No Proposal here',
            decision_number=6,
        ))
        create(Builder('agenda_item').having(
            meeting=self.meeting2,
            title=u'Nahhh not here either',
            decision_number=7,
        ))

        create(Builder('agenda_item').having(
            meeting=self.meeting2,
            is_paragraph=True,
            title=u'I am a paragraph'))

        create(Builder('agenda_item').having(
            meeting=self.meeting_after,
            title=u'I am after period end',
            decision_number=1,
        ))

        # freeze date to make sure the default period is 2016
        with freeze(datetime(2016, 12, 3)):
            self.other_committee = create(Builder('committee')
                                          .within(self.container))
        self.other_committee_model = self.other_committee.load_model()
        self.other_period = create(Builder('period').having(
            title=u'2010',
            date_from=date(2010, 1, 1),
            date_to=date(2010, 12, 31),
            committee=self.other_committee_model))

        self.other_meeting = create(Builder('meeting').having(
            committee=self.other_committee_model,
            start=pytz.UTC.localize(datetime(2010, 12, 31, 18, 30)),
            protocol_start_page_number=33))
        create(Builder('agenda_item').having(
            meeting=self.other_meeting,
            title=u'I should not appear in the test-toc',
            decision_number=77,
        ))

    def test_toc_json_is_generated_correctly(self):
        self.assertEqual(
            self.expected_toc_json, AlphabeticalToc(self.period).get_json())

    @browsing
    def test_shows_statusmessage_when_no_template_is_configured(self, browser):
        url = self.period.get_url(self.committee)
        browser.login().open(url, view='alphabetical_toc')
        # when an error happens here, the view returns an error
        # and the page is reloaded in Javascript. Here we reload manually
        browser.open(url)
        self.assertEqual(u'There is no toc template configured, toc could '
                         'not be generated.',
                         error_messages()[0])

    @browsing
    def test_toc_json_can_be_downloaded_only_by_managers(self, browser):
        url = self.period.get_url(self.committee)
        with self.assertRaises(InsufficientPrivileges):
            browser.login().open(url, view='alphabetical_toc/as_json')

        self.grant('Manager')
        browser.login().open(url, view='alphabetical_toc/as_json')
        self.assertEqual(self.expected_toc_json, browser.json)

    @browsing
    def test_toc_can_be_downloaded(self, browser):
        templates = create(Builder('templatefolder'))
        sablon_template = create(Builder('sablontemplate')
                                 .within(templates)
                                 .with_asset_file('sablon_template.docx'))
        self.committee.toc_template = RelationValue(
            getUtility(IIntIds).getId(sablon_template))
        transaction.commit()

        browser.login().open(self.committee,
                             view='tabbedview_view-periods')
        browser.find('download TOC alphabetical').click()

        self.assertDictContainsSubset(
            {'status': '200 Ok',
             'content-disposition': 'attachment; '
                'filename="Alphabetical Toc 2010 my-committee.docx"',
             'x-frame-options': 'SAMEORIGIN',
             'content-type': MIME_DOCX,
             'x-theme-disabled': 'True'},
            browser.headers)
        self.assertIsNotNone(browser.contents)


class TestTOCByRepository(TestAlphabeticalTOC):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER
    maxDiff = None

    expected_toc_json = {'toc': [{
        'group_title': None,
        'contents': [{
                'title': u'Nahhh not here either',
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 7,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }, {
                'title': u'No Proposal here',
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 6,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }]
        }, {
            'group_title': u'Business',
            'contents': [{
                'title': u'proposal 1',
                'dossier_reference_number': u'1.1.4 / 1',
                'repository_folder_title': u'Business',
                'meeting_date': '01.01.2010',
                'decision_number': 2,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }, {
                'title': u'\xdchhh',
                'dossier_reference_number': '1.1.4 / 2',
                'repository_folder_title': 'Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 3,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }]
        }, {
            'group_title': u'Other Stuff',
            'contents': [{
                'title': u'Anything goes',
                'dossier_reference_number': '3.1.4 / 77',
                'repository_folder_title': 'Other Stuff',
                'meeting_date': u'31.12.2010',
                'decision_number': 5,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }, {
            'group_title': u'Stuff',
            'contents': [{
                'title': u'Proposal 3',
                'dossier_reference_number': '2.1.4 / 1',
                'repository_folder_title': 'Stuff',
                'meeting_date': u'31.12.2010',
                'decision_number': 4,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }
    ]}

    def test_toc_json_is_generated_correctly(self):
        self.assertEqual(
            self.expected_toc_json, RepositoryBasedTOC(self.period).get_json())

    @browsing
    def test_shows_statusmessage_when_no_template_is_configured(self, browser):
        url = self.period.get_url(self.committee)
        browser.login().open(url, view='repository_toc')
        # when an error happens here, the view returns an error
        # and the page is reloaded in Javascript. Here we reload manually
        browser.open(url)
        self.assertEqual(u'There is no toc template configured, toc could '
                         'not be generated.',
                         error_messages()[0])

    @browsing
    def test_toc_json_can_be_downloaded_only_by_managers(self, browser):
        url = self.period.get_url(self.committee)
        with self.assertRaises(InsufficientPrivileges):
            browser.login().open(url, view='repository_toc/as_json')

        self.grant('Manager')
        browser.login().open(url, view='repository_toc/as_json')
        self.assertEqual(self.expected_toc_json, browser.json)

    @browsing
    def test_toc_can_be_downloaded(self, browser):
        templates = create(Builder('templatefolder'))
        sablon_template = create(Builder('sablontemplate')
                                 .within(templates)
                                 .with_asset_file('sablon_template.docx'))
        self.committee.toc_template = RelationValue(
            getUtility(IIntIds).getId(sablon_template))
        transaction.commit()

        browser.login().open(self.committee,
                             view='tabbedview_view-periods')
        browser.find('download TOC by repository').click()

        self.assertDictContainsSubset(
            {'status': '200 Ok',
             'content-disposition': 'attachment; '
                'filename="Repository Toc 2010 my-committee.docx"',
             'x-frame-options': 'SAMEORIGIN',
             'content-type': MIME_DOCX,
             'x-theme-disabled': 'True'},
            browser.headers)
        self.assertIsNotNone(browser.contents)
