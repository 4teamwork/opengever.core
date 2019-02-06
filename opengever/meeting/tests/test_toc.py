from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import InsufficientPrivileges
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testing import freeze
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.toc.alphabetical import AlphabeticalToc
from opengever.meeting.toc.dossier_refnum import DossierReferenceNumberBasedTOC
from opengever.meeting.toc.repository import RepositoryBasedTOC
from opengever.meeting.toc.repository_refnum import RepositoryReferenceNumberBasedTOC
from opengever.meeting.toc.utils import first_title_char
from opengever.meeting.toc.utils import normalise_string
from opengever.meeting.toc.utils import repo_refnum
from opengever.meeting.toc.utils import to_human_sortable_key
from opengever.testing import FunctionalTestCase
from plone import api
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import pytz
import transaction
import unittest


class TestFirstTitleChar(unittest.TestCase):

    def test_returns_the_first_character_of_title_key(self):
        item = {"title": u"test title", "other": u"another one"}
        self.assertEqual(first_title_char(item), u"t")

    def test_supports_plain_string(self):
        item = {"title": "test title"}
        self.assertEqual(first_title_char(item), u"t")

    def test_returns_lower_case(self):
        item = {"title": u'A test'}
        self.assertEqual(first_title_char(item), u'a')

    def test_umlauts_removed(self):
        item = {"title": u'\xe4'}
        self.assertEqual(first_title_char(item), u'a')


class TestRepoRefNum(FunctionalTestCase):

    def test_splits_dossier_refnum_correctly_for_dotted_formatter(self):
        api.portal.set_registry_record(
            name='formatter', value='dotted',
            interface=IReferenceNumberSettings)
        item = {'dossier_reference_number': "fd 1.2.1 / 1.2 / 2"}
        self.assertEqual("fd 1.2.1", repo_refnum(item))

    def test_splits_dossier_refnum_correctly_for_no_client_id_dotted_formatter(self):
        api.portal.set_registry_record(
            name='formatter', value='no_client_id_dotted',
            interface=IReferenceNumberSettings)
        item = {'dossier_reference_number': "1.2.1 / 1.2 / 2"}
        self.assertEqual("1.2.1", repo_refnum(item))

    def test_splits_dossier_refnum_correctly_for_grouped_by_three_formatter(self):
        api.portal.set_registry_record(
            name='formatter', value='grouped_by_three',
            interface=IReferenceNumberSettings)
        item = {'dossier_reference_number': "fd 134.3-2.1"}
        self.assertEqual("fd 134.3", repo_refnum(item))

    def test_splits_dossier_refnum_correctly_for_no_client_id_grouped_by_three_formatter(self):
        api.portal.set_registry_record(
            name='formatter', value='no_client_id_grouped_by_three',
            interface=IReferenceNumberSettings)
        item = {'dossier_reference_number': "134.3-2.1"}
        self.assertEqual("134.3", repo_refnum(item))


class TestNormaliseString(unittest.TestCase):

    def test_supports_empty_string(self):
        string = None
        self.assertEqual(normalise_string(string), None)

    def test_supports_plain_string(self):
        string = "test"
        self.assertEqual(normalise_string(string), u"test")

    def test_returns_lower_case(self):
        string = u'A tEst'
        self.assertEqual(normalise_string(string), u'a test')

    def test_removes_umlauts(self):
        string = u'\xe4'
        self.assertEqual(normalise_string(string), u'a')

    def test_supports_decomposed_unicode(self):
        string = u'a\u0308'
        self.assertEqual(normalise_string(string), u'a')


class TestHumanSorting(FunctionalTestCase):

    def test_sorts_numbers_correctly_for_dotted_formatter(self):
        unsorted = ["a 12.1 / 3.2 / 1.2", "b 9.3 / 10.1", "a 9.3 / 10.1", "b 9.3 / 1.1", "a 1.2.2 / 10.2"]
        expected = ["a 1.2.2 / 10.2", "a 9.3 / 10.1", "a 12.1 / 3.2 / 1.2", "b 9.3 / 1.1", "b 9.3 / 10.1"]
        self.assertEqual(sorted(unsorted, key=to_human_sortable_key),
                         expected)

    def test_sorts_numbers_correctly_for_grouped_by_three_formatter(self):
        api.portal.set_registry_record(
            name='formatter', value='grouped_by_three',
            interface=IReferenceNumberSettings)
        unsorted = ["a 121.2-3.2-12", "b 932.10-10.1", "b 932.9-10.1", "b 932.9-1.1", "a 932.9-10.1"]
        expected = ["a 121.2-3.2-12", "b 932.10-10.1", "b 932.9-1.1", "b 932.9-10.1", "a 932.9-10.1"]
        self.assertEqual(sorted(unsorted, key=to_human_sortable_key),
                         expected)

    def test_sorts_numbers_correctly_for_no_client_id_dotted_formatter(self):
        api.portal.set_registry_record(
            name='formatter', value='no_client_id_dotted',
            interface=IReferenceNumberSettings)
        unsorted = ["12.1 / 3.2 / 1.2", "9.3 / 10.1", "9.3 / 9.1", "9.3 / 1.1", "1.2.2 / 10.2"]
        expected = ["1.2.2 / 10.2", "9.3 / 1.1", "9.3 / 9.1", "9.3 / 10.1", "12.1 / 3.2 / 1.2"]
        self.assertEqual(sorted(unsorted, key=to_human_sortable_key),
                         expected)

    def test_sorts_numbers_correctly_for_no_client_id_grouped_by_three_formatter(self):
        api.portal.set_registry_record(
            name='formatter', value='no_client_id_grouped_by_three',
            interface=IReferenceNumberSettings)
        unsorted = ["121.2-3.2-12", "932.10-10.1", "932.9-10.1", "932.9-1.1", "932.9-9.1"]
        expected = ["121.2-3.2-12", "932.10-10.1", "932.9-1.1", "932.9-9.1", "932.9-10.1"]
        self.assertEqual(sorted(unsorted, key=to_human_sortable_key),
                         expected)


class TestAlphabeticalTOC(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER
    maxDiff = None

    view_name = 'alphabetical_toc'
    toc_class = AlphabeticalToc
    toc_filename = 'Alphabetical Toc 2010 my-committee.docx'
    download_button_label = 'download TOC alphabetical'

    expected_toc_json = {'toc': [{
        'group_title': u'A',
        'contents': [
            {
                'title': u'aa proposal',
                'description': None,
                'dossier_reference_number': '1.1.4 / 1',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 8,
                'has_proposal': True,
                'meeting_start_page_number': 33,
                }, {
                'title': u'\xc4a proposal',
                'description': None,
                'dossier_reference_number': '1.1.4 / 2',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 3,
                'has_proposal': True,
                'meeting_start_page_number': 33,
                }, {
                'title': u'Anything goes',
                'description': u'Really, Anything.',
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
                'description': u'But a description!',
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 7,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }, {
                'title': u'No Proposal here',
                'description': None,
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
                'description': None,
                'dossier_reference_number': u'1.1.4 / 1',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': '01.01.2010',
                'decision_number': 2,
                'has_proposal': True,
                'meeting_start_page_number': 33,
                }, {
                'title': u'Proposal 3',
                'description': None,
                'dossier_reference_number': '10.1.4 / 1',
                'repository_folder_title': 'A Business',
                'meeting_date': u'31.12.2010',
                'decision_number': 4,
                'has_proposal': True,
                'meeting_start_page_number': 129,
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
            repository_folder_title=u'\xc4 Business',
            dossier_reference_number='1.1.4 / 1',
            int_id=1).within(self.committee))
        proposal1_2 = create(Builder('submitted_proposal').having(
            title=u'\xc4a proposal',
            repository_folder_title=u'\xc4 Business',
            dossier_reference_number='1.1.4 / 2',
            int_id=2).within(self.committee))
        proposal1_3 = create(Builder('submitted_proposal').having(
            title=u'aa proposal',
            repository_folder_title=u'\xc4 Business',
            dossier_reference_number='1.1.4 / 1',
            int_id=5).within(self.committee))

        proposal2_1 = create(Builder('submitted_proposal').having(
            title=u'Proposal 3',
            repository_folder_title='A Business',
            dossier_reference_number='10.1.4 / 1',
            int_id=3).within(self.committee))
        proposal2_2 = create(Builder('submitted_proposal').having(
            title=u'Anything goes',
            description=u'Really, Anything.',
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
            meeting=self.meeting1,
            proposal=proposal1_3,
            decision_number=8,
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
            description=u'But a description!',
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
        self.assertDictEqual(
            self.expected_toc_json, self.toc_class(self.period).get_json(),
            "Toc mismatch in {}".format(self.toc_class.__name__))

    @browsing
    def test_shows_statusmessage_when_no_template_is_configured(self, browser):
        url = self.period.get_url(self.committee)
        browser.login().open(url, view=self.view_name)
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
            browser.login().open(url, view='{}/as_json'.format(self.view_name))

        self.grant('Manager')
        browser.login().open(url, view='{}/as_json'.format(self.view_name))
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
        browser.find(self.download_button_label).click()

        self.assertDictContainsSubset(
            {'status': '200 Ok',
             'content-disposition': 'attachment; '
                'filename="{}"'.format(self.toc_filename),
             'x-frame-options': 'SAMEORIGIN',
             'content-type': MIME_DOCX,
             'x-theme-disabled': 'True'},
            browser.headers)
        self.assertIsNotNone(browser.contents)


class TestTOCByRepository(TestAlphabeticalTOC):

    view_name = 'repository_toc'
    toc_class = RepositoryBasedTOC
    toc_filename = 'Repository Toc 2010 my-committee.docx'
    download_button_label = 'download TOC by repository'

    expected_toc_json = {'toc': [{
        'group_title': u'Ad hoc agendaitems',
        'contents': [{
                'title': u'Nahhh not here either',
                'description': u'But a description!',
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 7,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }, {
                'title': u'No Proposal here',
                'description': None,
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 6,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }]
        }, {
            'group_title': u'A Business',
            'contents': [{
                'title': u'Proposal 3',
                'description': None,
                'dossier_reference_number': '10.1.4 / 1',
                'repository_folder_title': 'A Business',
                'meeting_date': u'31.12.2010',
                'decision_number': 4,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }, {
            'group_title': u'\xc4 Business',
            'contents': [{
                'title': u'aa proposal',
                'description': None,
                'dossier_reference_number': '1.1.4 / 1',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 8,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }, {
                'title': u'\xc4a proposal',
                'description': None,
                'dossier_reference_number': '1.1.4 / 2',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 3,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }, {
                'title': u'proposal 1',
                'description': None,
                'dossier_reference_number': u'1.1.4 / 1',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': '01.01.2010',
                'decision_number': 2,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }]
        }, {
            'group_title': u'Other Stuff',
            'contents': [{
                'title': u'Anything goes',
                'description': u'Really, Anything.',
                'dossier_reference_number': '3.1.4 / 77',
                'repository_folder_title': 'Other Stuff',
                'meeting_date': u'31.12.2010',
                'decision_number': 5,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }]
    }


class TestTOCByDossierReferenceNumber(TestAlphabeticalTOC):

    view_name = 'dossier_refnum_toc'
    toc_class = DossierReferenceNumberBasedTOC
    toc_filename = 'Dossier Reference Number Toc 2010 my-committee.docx'
    download_button_label = 'download TOC by dossier reference number'

    expected_toc_json = {'toc': [{
        'group_title': u'Ad hoc agendaitems',
        'contents': [{
                'title': u'Nahhh not here either',
                'description': u'But a description!',
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 7,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }, {
                'title': u'No Proposal here',
                'description': None,
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 6,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }]
        }, {
            'group_title': u'1.1.4 / 1',
            'contents': [{
                'title': u'aa proposal',
                'description': None,
                'dossier_reference_number': '1.1.4 / 1',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 8,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }, {
                'title': u'proposal 1',
                'description': None,
                'dossier_reference_number': u'1.1.4 / 1',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': '01.01.2010',
                'decision_number': 2,
                'has_proposal': True,
                'meeting_start_page_number': 33,
             }]
        }, {
            'group_title': u'1.1.4 / 2',
            'contents': [{
                'title': u'\xc4a proposal',
                'description': None,
                'dossier_reference_number': '1.1.4 / 2',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 3,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }]
        }, {
            'group_title': u'3.1.4 / 77',
            'contents': [{
                'title': u'Anything goes',
                'description': u'Really, Anything.',
                'dossier_reference_number': '3.1.4 / 77',
                'repository_folder_title': 'Other Stuff',
                'meeting_date': u'31.12.2010',
                'decision_number': 5,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }, {
            'group_title': u'10.1.4 / 1',
            'contents': [{
                'title': u'Proposal 3',
                'description': None,
                'dossier_reference_number': '10.1.4 / 1',
                'repository_folder_title': 'A Business',
                'meeting_date': u'31.12.2010',
                'decision_number': 4,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }]
    }


class TestTOCByRepositoryReferenceNumber(TestAlphabeticalTOC):

    view_name = 'repository_refnum_toc'
    toc_class = RepositoryReferenceNumberBasedTOC
    toc_filename = 'Repository Reference Number Toc 2010 my-committee.docx'
    download_button_label = 'download TOC by repository reference number'

    expected_toc_json = {'toc': [{
        'group_title': u'Ad hoc agendaitems',
        'contents': [{
                'title': u'Nahhh not here either',
                'description': u'But a description!',
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 7,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }, {
                'title': u'No Proposal here',
                'description': None,
                'dossier_reference_number': None,
                'repository_folder_title': None,
                'meeting_date': u'31.12.2010',
                'decision_number': 6,
                'has_proposal': False,
                'meeting_start_page_number': 129,
            }]
        }, {
            'group_title': u'1.1.4',
            'contents': [{
                'title': u'aa proposal',
                'description': None,
                'dossier_reference_number': '1.1.4 / 1',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 8,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }, {
                'title': u'\xc4a proposal',
                'description': None,
                'dossier_reference_number': '1.1.4 / 2',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': u'01.01.2010',
                'decision_number': 3,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }, {
                'title': u'proposal 1',
                'description': None,
                'dossier_reference_number': u'1.1.4 / 1',
                'repository_folder_title': u'\xc4 Business',
                'meeting_date': '01.01.2010',
                'decision_number': 2,
                'has_proposal': True,
                'meeting_start_page_number': 33,
            }]
        }, {
            'group_title': u'3.1.4',
            'contents': [{
                'title': u'Anything goes',
                'description': u'Really, Anything.',
                'dossier_reference_number': '3.1.4 / 77',
                'repository_folder_title': 'Other Stuff',
                'meeting_date': u'31.12.2010',
                'decision_number': 5,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }, {
            'group_title': u'10.1.4',
            'contents': [{
                'title': u'Proposal 3',
                'description': None,
                'dossier_reference_number': '10.1.4 / 1',
                'repository_folder_title': 'A Business',
                'meeting_date': u'31.12.2010',
                'decision_number': 4,
                'has_proposal': True,
                'meeting_start_page_number': 129,
            }]
        }]
    }
