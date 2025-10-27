from ftw.testbrowser import browsing
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from os.path import join as pjoin
from plone.namedfile.file import NamedBlobFile
from plone.restapi.serializer.converters import json_compatible
import json


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
             u'modified': None,
             u'modifier': None,
             u'additional_data':{},
             u'response_id': response_id,
             u'response_type': u'created',
             u'text': u''},
            responses[0])

    @browsing
    def test_proposal_contains_committee(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.proposal, method="GET", headers=self.api_headers)
        self.assertEqual({u'@id': self.committee.absolute_url(),
                          u'title': self.committee.title}, browser.json['committee'])

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
             u'modified': None,
             u'modifier': None,
             u'additional_data':{},
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
             u'modified': None,
             u'modifier': None,
             u'additional_data':{},
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
             u'UID': u'createmeetings000000000000000005',
             u'checked_out': None,
             u'description': u'',
             u'file_extension': u'.docx',
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
             u'UID': u'createmeetings000000000000000004',
             u'checked_out': None,
             u'description': u'',
             u'file_extension': u'.docx',
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
             u'UID': successor_proposal.UID(),
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
             u'UID': proposal.UID(),
             u'description': u'',
             u'is_leafnode': None,
             u'review_state': u'proposal-state-decided',
             u'title': proposal.title},
            browser.json['predecessor_proposal'])


class TestSubmitAdditionalDocuments(IntegrationTestCase):

    features = (
        'meeting',
    )

    @browsing
    def test_documents_parameter_is_mandatory(self, browser):
        self.login(self.meeting_user, browser=browser)
        proposal = self.decided_proposal.load_model().resolve_proposal()

        data = json.dumps({})

        with browser.expect_http_error(reason='Bad Request'):
            browser.open(proposal, view="@submit-additional-documents",
                         method='POST', headers=self.api_headers, data=data)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'message': u'Missing parameter: documents',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_documents_cannot_be_empty_list(self, browser):
        self.login(self.meeting_user, browser=browser)
        proposal = self.decided_proposal.load_model().resolve_proposal()

        data = json.dumps({
            'documents': []
        })

        with browser.expect_http_error(reason='Bad Request'):
            browser.open(proposal, view="@submit-additional-documents",
                         method='POST', headers=self.api_headers, data=data)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'message': u'Missing parameter: documents',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_can_only_submit_document_from_main_dossier(self, browser):
        self.login(self.meeting_user, browser=browser)
        proposal = self.decided_proposal.load_model().resolve_proposal()

        data = json.dumps({
            'documents': [self.resolvable_document.UID()]
        })

        with browser.expect_http_error(reason='Bad Request'):
            browser.open(proposal, view="@submit-additional-documents",
                         method='POST', headers=self.api_headers, data=data)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'message': u'Only documents within main dossier are allowed',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_user_can_only_submit_documents_he_can_view(self, browser):
        self.login(self.meeting_user, browser=browser)
        proposal = self.decided_proposal.load_model().resolve_proposal()

        data = json.dumps({
            'documents': [self.subdocument.UID()]
        })

        self.subdossier.__ac_local_roles_block__ = True

        with browser.expect_http_error(reason='Unauthorized'):
            browser.open(proposal, view="@submit-additional-documents",
                         method='POST', headers=self.api_headers, data=data)

        self.assertEqual(401, browser.status_code)
        self.assertEqual(
            {u'message': u"You are not allowed to access '{}' in this context"
                         u"".format(self.subdocument.id),
             u'type': u'Unauthorized'},
            browser.json)

    @browsing
    def test_submitting_additional_documents(self, browser):
        self.login(self.meeting_user, browser=browser)

        model = self.proposal.load_model()
        self.assertEqual(1, len(model.submitted_documents))
        documents = model.resolve_submitted_proposal().get_documents()
        self.assertEqual(1, len(documents))

        previously_submitted = documents[0]

        data = json.dumps({
            'documents': [self.subdocument.UID(), self.mail_eml.UID()]
        })

        with self.observe_children(self.submitted_proposal) as children:
            browser.open(self.proposal, view="@submit-additional-documents",
                         method='POST', headers=self.api_headers, data=data)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [{u'action': u'copied',
              u'source': self.subdocument.absolute_url()},
             {u'action': u'copied',
              u'source': self.mail_eml.absolute_url()}],
            browser.json)

        self.assertEqual(2, len(children["added"]))
        self.assertEqual(3, len(model.submitted_documents))
        documents = model.resolve_submitted_proposal().get_documents()
        self.assertEqual(3, len(documents))
        self.assertItemsEqual(list(children['added']) + [previously_submitted],
                              documents)

    @browsing
    def test_submitting_additional_document_already_up_to_date(self, browser):
        self.login(self.meeting_user, browser=browser)

        data = json.dumps({
            'documents': [self.document.UID()]
        })

        browser.open(self.proposal, view="@submit-additional-documents",
                     method='POST', headers=self.api_headers, data=data)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [{u'action': None,
              u'source': self.document.absolute_url()}],
            browser.json)

    @browsing
    def test_submitting_additional_document_new_version(self, browser):
        self.login(self.meeting_user, browser=browser)

        model = self.proposal.load_model()
        self.assertEqual(1, len(model.submitted_documents))
        documents = model.resolve_submitted_proposal().get_documents()
        self.assertEqual(1, len(documents))
        self.assertEqual(documents[0].file.data,
                         self.document.file.data)

        versioner = Versioner(self.document)
        versioner.create_initial_version()
        self.document.file = NamedBlobFile(data='New', filename=u'test.txt')
        versioner.create_version("new version")

        model = self.proposal.load_model()
        self.assertEqual(1, len(model.submitted_documents))
        documents = model.resolve_submitted_proposal().get_documents()
        self.assertEqual(1, len(documents))
        self.assertNotEqual(documents[0].file.data,
                            self.document.file.data)

        data = json.dumps({
            'documents': [self.document.UID()]
        })

        browser.open(self.proposal, view="@submit-additional-documents",
                     method='POST', headers=self.api_headers, data=data)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            [{u'action': u'updated',
              u'source': self.document.absolute_url()}],
            browser.json)

        model = self.proposal.load_model()
        self.assertEqual(1, len(model.submitted_documents))
        documents = model.resolve_submitted_proposal().get_documents()
        self.assertEqual(1, len(documents))
        self.assertEqual(documents[0].file.data,
                         self.document.file.data)
        self.assertEqual("New", documents[0].file.data)


class TestRISExcerptEndpoints(IntegrationTestCase):

    @browsing
    def test_ris_return_and_update_excerpt(self, browser):
        self.login(self.regular_user, browser)

        dossier_rel = "/".join(self.dossier.getPhysicalPath()[2:])

        browser.open(
            self.document.absolute_url() + "/@ris-return-excerpt",
            method="POST",
            headers=self.api_headers,
            data=json.dumps(
                {
                    "target_admin_unit_id": "plone",
                    "target_dossier_relative_path": dossier_rel,
                }
            ),
        )

        self.assertEqual(200, browser.status_code)
        data = browser.json
        self.assertEqual(data["current_version_id"], 0)

        excerpt_doc = self.portal.unrestrictedTraverse(data["path"].encode("utf-8"))

        self.assertEqual(excerpt_doc.file.data, self.document.file.data)
        self.assertTrue(excerpt_doc.is_final_document())

        browser.open(
            self.document.absolute_url() + "/@ris-update-excerpt",
            method="POST",
            headers=self.api_headers,
            data=json.dumps(
                {
                    "target_admin_unit_id": "plone",
                    "target_doc_relative_path": data["path"],
                }
            ),
        )

        self.assertEqual(browser.json["current_version_id"], 1)
        self.assertTrue(excerpt_doc.is_final_document())
