from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from mock import patch
from mock import PropertyMock
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseContainer
from opengever.document.approvals import IApprovalList
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.task.browser.accept.utils import accept_task_with_successor
from opengever.testing import IntegrationTestCase
from plone import api
from plone.uuid.interfaces import IUUID
from z3c.relationfield.relation import RelationValue
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.intid import IIntIds
import json


class TestCompleteSuccessorTaskPost(IntegrationTestCase):

    def prepare_accepted_task_pair(self, task_type='correction'):
        predecessor = create(
            Builder('task')
            .within(self.dossier)
            .having(issuer=self.dossier_responsible.id,
                    responsible=self.regular_user.id,
                    responsible_client='fa',
                    task_type=task_type)
            .in_state('task-state-open')
            .titled(u'Inquiry from a concerned citizen'))

        sql_task = predecessor.get_sql_object()

        successor = accept_task_with_successor(
            self.dossier,
            'plone:%s' % sql_task.int_id,
            u'I accept this task',
        )
        return predecessor, successor

    def last_response(self, obj):
        return IResponseContainer(obj).list()[-1]

    @browsing
    def test_invoking_complete_successor_task_requires_modify_portal_content(self, browser):
        self.login(self.regular_user)
        url = '{}/@complete-successor-task'.format(self.task.absolute_url())
        self.logout()

        # Merely invoking the endpoint requires Modify Portal Content.
        # The required permission checks on the remote side will then
        # be performed as usual, the endpoint just proxies the request
        # in the security context of the user.
        with browser.expect_http_error(code=401):
            browser.open(url, method='POST', headers=self.api_headers)

    @browsing
    def test_requires_transition_parameter(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@complete-successor-task'.format(self.task.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Required parameter "transition" is missing in body'},
            browser.json)

    @browsing
    def test_rejects_unexpected_parameters(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@complete-successor-task'.format(self.task.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({
                    'transition': '<irrelevant>',
                    'unexpected': 'garbage',
                }),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Unexpected parameter(s) in JSON body: ["unexpected"]. '
                         u'Supported parameters are: ["transition", "documents", "text", "approved_documents", "pass_documents_to_next_task"]'},
            browser.json)

    @browsing
    def test_requires_task_with_predecessor(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@complete-successor-task'.format(self.task.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'transition': '<irrelevant>'}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'@complete-successor-task only supports successor '
                         u'tasks. This task has no predecessor.'},
            browser.json)

    @browsing
    def test_delivers_documents_and_mails(self, browser):
        self.login(self.regular_user, browser)

        # Test setup - create predecessor and accepted successor task pair
        predecessor, successor = self.prepare_accepted_task_pair()

        # Add a document and mail in successor that should be delivered back
        procuded_mail = create(Builder('mail')
                               .within(self.dossier)
                               .with_asset_message('mail_with_one_mail_attachment.eml'))
        produced_doc = create(Builder('document')
                              .within(successor)
                              .titled(u'Statement in response to inquiry')
                              .with_asset_file('text.txt'))

        self.login(self.regular_user, browser)
        # Need to trick the transition controller into thinking its a remote
        # request so that it allows the resolve transition on the predecessor
        with patch('opengever.task.browser.transitioncontroller.'
                   'RequestChecker.is_remote',
                   new_callable=PropertyMock) as mock_is_remote:
            mock_is_remote.return_value = True

            request_body = json.dumps({
                'transition': 'task-transition-in-progress-resolved',
                'text': 'I finished this task.',
                'documents': [getUtility(IIntIds).getId(produced_doc),
                              getUtility(IIntIds).getId(procuded_mail)]
            })
            with self.observe_children(predecessor) as children:
                browser.open(
                    successor.absolute_url() + '/@complete-successor-task',
                    method='POST',
                    data=request_body,
                    headers=self.api_headers)

        self.assertEqual(2, len(children["added"]))
        self.assertItemsEqual(
            ['RE: Statement in response to inquiry',
             'RE: \xc3\x84usseres Testm\xc3\xa4il'],
            [obj.Title() for obj in children["added"]])

    @browsing
    def test_prevents_checked_out_documents(self, browser):
        self.login(self.regular_user, browser)

        # Test setup - create predecessor and accepted successor task pair
        predecessor, successor = self.prepare_accepted_task_pair()

        # Add a document in successor that is supposed to be delivered back
        produced_doc = create(Builder('document')
                              .within(successor)
                              .titled(u'Statement in response to inquiry')
                              .attach_file_containing(
                                  'Statement text',
                                  u'statement.docx'))

        self.login(self.dossier_responsible, browser)
        manager = getMultiAdapter((produced_doc, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        self.login(self.regular_user, browser)
        # Need to trick the transition controller into thinking its a remote
        # request so that it allows the resolve transition on the predecessor
        with patch('opengever.task.browser.transitioncontroller.'
                   'RequestChecker.is_remote',
                   new_callable=PropertyMock) as mock_is_remote:
            mock_is_remote.return_value = True

            request_body = json.dumps({
                'transition': 'task-transition-in-progress-resolved',
                'text': 'I finished this task.',
                'documents': [getUtility(IIntIds).getId(produced_doc)]
            })
            with browser.expect_http_error(code=400):
                browser.open(
                    successor.absolute_url() + '/@complete-successor-task',
                    method='POST',
                    data=request_body,
                    headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Some documents are checked out.'},
            browser.json)

    @browsing
    def test_approves_document_if_given(self, browser):
        self.login(self.regular_user, browser)

        # Test setup - create predecessor and accepted successor task pair
        predecessor, successor = self.prepare_accepted_task_pair(
            task_type='approval')

        # Add a document in successor that is supposed to be delivered back
        doc = create(Builder('document')
                     .within(successor)
                     .titled(u'Statement in response to inquiry'))

        # Need to trick the transition controller into thinking its a remote
        # request so that it allows the resolve transition on the predecessor
        with patch('opengever.task.browser.transitioncontroller.'
                   'RequestChecker.is_remote',
                   new_callable=PropertyMock) as mock_is_remote:
            mock_is_remote.return_value = True

            request_body = json.dumps({
                'transition': 'task-transition-in-progress-resolved',
                'text': 'I finished this task.',
                'approved_documents': [IUUID(doc)]
            })
            browser.open(
                successor.absolute_url() + '/@complete-successor-task',
                method='POST',
                data=request_body,
                headers=self.api_headers)

        # Predecessor and successor should have been closed
        self.assertEqual('task-state-resolved', api.content.get_state(predecessor))
        self.assertEqual('task-state-resolved', api.content.get_state(successor))

        approvals = IApprovalList(doc).get()
        self.assertEqual(1, len(approvals))
        self.assertEqual(IUUID(successor), approvals[0].task_uid)

    @browsing
    def test_pass_documents_to_next_task_if_selected(self, browser):
        self.login(self.regular_user, browser)

        self.seq_subtask_1.task_type = 'correction'
        self.seq_subtask_1.sync()

        successor = accept_task_with_successor(
            self.dossier,
            'plone:%s' % self.seq_subtask_1.get_sql_object().int_id,
            u'I accept this task')

        intids = getUtility(IIntIds)
        self.seq_subtask_1.relatedItems = [RelationValue(intids.getId(self.document)), ]

        # Need to trick the transition controller into thinking its a remote
        # request so that it allows the resolve transition on the predecessor
        with patch('opengever.task.browser.transitioncontroller.'
                   'RequestChecker.is_remote',
                   new_callable=PropertyMock) as mock_is_remote:
            mock_is_remote.return_value = True

            request_body = json.dumps({
                'transition': 'task-transition-in-progress-resolved',
                'text': 'I finished this task.',
                'pass_documents_to_next_task': True,
            })
            browser.open(
                successor.absolute_url() + '/@complete-successor-task',
                method='POST',
                data=request_body,
                headers=self.api_headers)

        # Predecessor and successor should have been closed
        self.assertEqual('task-state-resolved',
                         api.content.get_state(self.seq_subtask_1))
        self.assertEqual('task-state-resolved', api.content.get_state(successor))

        # relatedItems are passed to sequential successor
        self.assertEqual(1, len(self.seq_subtask_2.relatedItems))
        self.assertEqual(self.document, self.seq_subtask_2.relatedItems[0].to_object)

    @browsing
    def test_complete_successor_task_closes_predecessor(self, browser):
        self.login(self.regular_user, browser)

        # Test setup - create predecessor and accepted successor task pair
        predecessor, successor = self.prepare_accepted_task_pair()

        # Add a document in successor that is supposed to be delivered back
        produced_doc = create(Builder('document')
                              .within(successor)
                              .titled(u'Statement in response to inquiry')
                              .attach_file_containing(
                                  'Statement text',
                                  u'statement.docx'))

        int_ids = getUtility(IIntIds)
        produced_doc_intid = int_ids.getId(produced_doc)

        # Need to trick the transition controller into thinking its a remote
        # request so that it allows the resolve transition on the predecessor
        with patch('opengever.task.browser.transitioncontroller.'
                   'RequestChecker.is_remote',
                   new_callable=PropertyMock) as mock_is_remote:
            mock_is_remote.return_value = True

            request_body = json.dumps({
                'transition': 'task-transition-in-progress-resolved',
                'text': 'I finished this task.',
                'documents': [produced_doc_intid]
            })
            browser.open(
                successor.absolute_url() + '/@complete-successor-task',
                method='POST',
                data=request_body,
                headers=self.api_headers)

        # Predecessor and successor should have been closed
        self.assertEqual('task-state-resolved', api.content.get_state(predecessor))
        self.assertEqual('task-state-resolved', api.content.get_state(successor))

        # Response text should be on predecessor and successor
        self.assertEqual(u'I finished this task.', self.last_response(predecessor).text)
        self.assertEqual(u'I finished this task.', self.last_response(successor).text)

        # Delivered document was copied to predecessor
        self.assertEqual(1, len(predecessor.objectValues()))
        self.assertEquals(
            u'RE: Statement in response to inquiry',
            predecessor.objectValues()[-1].title)

        # Delivered document is referenced from response on successor
        self.assertEqual(1, len(self.last_response(successor).added_objects))
        self.assertEqual(produced_doc, self.last_response(successor).added_objects[0].to_object)

        # Response body should contain serialized successor task, including
        # responses and copied documents

        response = browser.json

        self.assertDictContainsSubset({
            u'@id': successor.absolute_url(),
            u'@type': u'opengever.task.task',
            u'UID': successor.UID(),
            u'issuer': {u'title': u'Ziegler Robert (robert.ziegler)',
                        u'token': u'robert.ziegler'},
            u'oguid': str(successor.oguid),
            u'predecessor': str(predecessor.oguid),
            u'responsible': {u'title': u'Finanz\xe4mt: B\xe4rfuss K\xe4thi (kathi.barfuss)',
                             u'token': u'fa:kathi.barfuss'},
            u'responsible_client': {u'title': u'Finanz\xe4mt', u'token': u'fa'},
            u'review_state': u'task-state-resolved',
            u'revoke_permissions': True,
            u'task_type': {u'title': u'For your review',
                           u'token': u'correction'},
            u'title': u'Inquiry from a concerned citizen'},
            response)

        self.assertEqual([{
            u'@id': produced_doc.absolute_url(),
            u'@type': u'opengever.document.document',
            u'UID': produced_doc.UID(),
            u'checked_out': u'',
            u'description': u'',
            u'file_extension': u'.docx',
            u'is_leafnode': None,
            u'review_state': u'document-state-draft',
            u'title': produced_doc.title}],
            response['items'])

        self.assertDictContainsSubset({
            u'added_objects': [{u'@id': produced_doc.absolute_url(),
                                u'@type': u'opengever.document.document',
                                u'UID': produced_doc.UID(),
                                u'checked_out': None,
                                u'description': u'',
                                u'file_extension': u'.docx',
                                u'is_leafnode': None,
                                u'review_state': u'document-state-draft',
                                u'title': u'Statement in response to inquiry'}],
            u'changes': [],
            u'creator': {u'title': u'B\xe4rfuss K\xe4thi',
                         u'token': u'kathi.barfuss'},
            u'mimetype': u'',
            u'related_items': [],
            u'rendered_text': u'',
            u'response_type': u'default',
            u'successor_oguid': u'',
            u'text': u'I finished this task.',
            u'transition': u'task-transition-in-progress-resolved'},
            response['responses'][-1])

    @browsing
    def test_complete_successor_task_accepts_document_urls(self, browser):
        self.login(self.regular_user, browser)

        # Test setup - create predecessor and accepted successor task pair
        predecessor, successor = self.prepare_accepted_task_pair()

        # Add documents in successor that are supposed to be delivered back
        doc = create(Builder('document')
                     .within(successor)
                     .titled(u'Statement in response to inquiry'))

        # Need to trick the transition controller into thinking its a remote
        # request so that it allows the resolve transition on the predecessor
        with patch('opengever.task.browser.transitioncontroller.'
                   'RequestChecker.is_remote',
                   new_callable=PropertyMock) as mock_is_remote:
            mock_is_remote.return_value = True

            request_body = json.dumps({
                'transition': 'task-transition-in-progress-resolved',
                'text': 'I finished this task.',
                'documents': [doc.absolute_url()]
            })
            browser.open(
                successor.absolute_url() + '/@complete-successor-task',
                method='POST',
                data=request_body,
                headers=self.api_headers)

        self.assertEquals(
            u'RE: Statement in response to inquiry',
            predecessor.objectValues()[-1].title)

        # Delivered document is referenced from response on successor
        self.assertEqual(1, len(self.last_response(successor).added_objects))
        self.assertEqual(doc, self.last_response(successor).added_objects[0].to_object)

    def test_parses_intids_paths_and_oguids_as_doc_references(self):
        self.login(self.regular_user)

        endpoint = getMultiAdapter((self.task, self.request),
                                   name="POST_application_json_@complete-successor-task")

        resolve = endpoint._resolve_doc_ref_to_intid
        int_id = getUtility(IIntIds).getId(self.document)

        self.assertEqual(int_id, resolve(int_id))
        self.assertEqual(int_id, resolve(str(Oguid.for_object(self.document))))
        self.assertEqual(int_id, resolve(self.document.absolute_url_path().replace('/plone', '')))
        # self.assertEqual(int_id, resolve(self.document.absolute_url()))

        with self.assertRaises(BadRequest) as cm:
            resolve('garbage')
        self.assertEqual(
            "Unknown document reference: 'garbage'", str(cm.exception))
