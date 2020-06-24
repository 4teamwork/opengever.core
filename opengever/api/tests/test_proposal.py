from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from os.path import join as pjoin
from plone.restapi.serializer.converters import json_compatible


class TestProposalSerialization(IntegrationTestCase):

    features = (
        'meeting',
    )

    @browsing
    def test_proposal_contains_a_list_of_responses(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.proposal, method="GET", headers=self.api_headers)
        self.maxDiff = None
        responses = browser.json['responses']

        self.assertEquals(3, len(responses))

        response_id = 1472645373000000
        expected_path = pjoin(self.proposal.absolute_url(),
                              '@responses',
                              str(response_id))
        self.assertEquals(
            {u'@id': expected_path,
             u'additional_data': {},
             u'changes': [],
             u'created': json_compatible(self.proposal.created().utcdatetime()),
             u'creator': {u'title': u'Ziegler Robert', u'token': u'robert.ziegler'},
             u'response_id': response_id,
             u'response_type': u'created',
             u'text': u''},
            responses[0])

    @browsing
    def test_getting_specific_response_from_proposal(self, browser):
        self.login(self.regular_user, browser=browser)

        response_id = 1472645373000000
        url = pjoin(self.proposal.absolute_url(), '@responses', str(response_id))
        browser.open(url, method="GET", headers=self.api_headers)
        self.maxDiff = None

        self.assertEquals(
            {u'@id': url,
             u'additional_data': {},
             u'changes': [],
             u'created': json_compatible(self.proposal.created().utcdatetime()),
             u'creator': {u'title': u'Ziegler Robert', u'token': u'robert.ziegler'},
             u'response_id': response_id,
             u'response_type': u'created',
             u'text': u''},
            browser.json)

    @browsing
    def test_scheduled_response_contains_meeting_title_and_url(self, browser):
        self.login(self.meeting_user, browser=browser)
        response_id = 1472649453000000
        url = pjoin(self.decided_proposal.absolute_url(), '@responses', str(response_id))
        browser.open(url, method="GET", headers=self.api_headers)

        self.maxDiff = None
        self.assertEqual(u'scheduled', browser.json['response_type'])
        self.assertDictEqual(
            {u'meeting_id': self.decided_meeting.model.meeting_id,
             u'meeting_title': self.decided_meeting.get_title(),
             u'meeting_url': "{}/view".format(self.decided_meeting.absolute_url())},
            browser.json['additional_data'])

    @browsing
    def test_submitted_proposal_contains_a_list_of_responses(self, browser):
        self.login(self.meeting_user, browser=browser)
        browser.open(self.submitted_proposal, method="GET", headers=self.api_headers)
        self.maxDiff = None
        responses = browser.json['responses']

        self.assertEquals(2, len(responses))

        response_id = 1472645373000000
        expected_path = pjoin(self.submitted_proposal.absolute_url(),
                              '@responses',
                              str(response_id))
        self.assertEquals(
            {u'@id': expected_path,
             u'additional_data': {},
             u'changes': [],
             u'created': json_compatible(self.submitted_proposal.created().utcdatetime()),
             u'creator': {u'title': u'Ziegler Robert', u'token': u'robert.ziegler'},
             u'response_id': response_id,
             u'response_type': u'submitted',
             u'text': u''},
            responses[0])

    @browsing
    def test_decided_proposal_contains_meeting_decision_number_and_excerpt(self, browser):
        self.login(self.meeting_user, browser=browser)
        proposal = self.decided_proposal.load_model().resolve_proposal()

        browser.open(proposal, method="GET", headers=self.api_headers)

        self.assertIn(u'meeting', browser.json)
        self.assertDictEqual(
            {u'@id': self.decided_meeting.absolute_url(),
             u'title': self.decided_meeting.get_title()},
            browser.json[u'meeting'])

        self.assertIn(u'decision_number', browser.json)
        self.assertEqual(u'2016 / 1', browser.json[u'decision_number'])

        excerpt = proposal.get_excerpt()
        self.assertDictEqual(
            {u'@id': excerpt.absolute_url(),
             u'@type': u'opengever.document.document',
             u'description': u'',
             u'is_leafnode': None,
             u'review_state': u'document-state-draft',
             u'title': excerpt.title},
            browser.json[u'excerpt'])

    @browsing
    def test_decided_submitted_proposal_contains_meeting_decision_number_and_excerpt(self, browser):
        self.login(self.meeting_user, browser=browser)

        browser.open(self.decided_proposal, method="GET", headers=self.api_headers)

        self.assertIn(u'meeting', browser.json)
        self.assertDictEqual(
            {u'@id': self.decided_meeting.absolute_url(),
             u'title': self.decided_meeting.get_title()},
            browser.json[u'meeting'])

        self.assertIn(u'decision_number', browser.json)
        self.assertEqual(u'2016 / 1', browser.json[u'decision_number'])

        excerpt = self.decided_proposal.get_excerpt()
        self.assertDictEqual(
            {u'@id': excerpt.absolute_url(),
             u'@type': u'opengever.document.document',
             u'description': u'',
             u'is_leafnode': None,
             u'review_state': u'document-state-draft',
             u'title': excerpt.title},
            browser.json[u'excerpt'])

    @browsing
    def test_proposals_contain_successor_and_predecessor(self, browser):
        self.login(self.meeting_user, browser=browser)
        proposal = self.decided_proposal.load_model().resolve_proposal()

        browser.open(proposal, view='tabbedview_view-overview')
        browser.click_on('Create successor proposal')
        successor_title = u'\xc4nderungen am Personalreglement zur Nachpr\xfcfung'
        browser.fill({
            'Title': successor_title,
            'Proposal template': proposal.get_proposal_document().Title(),
        }).save()

        successor_proposal = browser.context

        browser.open(proposal, method="GET", headers=self.api_headers)
        self.assertIsNone(browser.json['predecessor_proposal'])
        self.assertEqual(1, len(browser.json['successor_proposals']))
        self.assertDictEqual(
            {u'@id': successor_proposal.absolute_url(),
             u'@type': u'opengever.meeting.proposal',
             u'description': u'',
             u'is_leafnode': None,
             u'review_state': u'proposal-state-active',
             u'title': successor_title},
            browser.json['successor_proposals'][0])

        browser.open(successor_proposal, method="GET", headers=self.api_headers)
        self.assertIsNotNone(browser.json['predecessor_proposal'])
        self.assertEqual(0, len(browser.json['successor_proposals']))
        self.assertDictEqual(
            {u'@id': proposal.absolute_url(),
             u'@type': u'opengever.meeting.proposal',
             u'description': u'',
             u'is_leafnode': None,
             u'review_state': u'proposal-state-decided',
             u'title': proposal.title},
            browser.json['predecessor_proposal'])
