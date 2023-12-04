from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from mock import patch
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseContainer
from opengever.testing import IntegrationTestCase
from plone import api
from unittest import skip
import json


class TestAcceptRemoteTaskPost(IntegrationTestCase):

    def last_response(self, obj):
        return IResponseContainer(obj).list()[-1]

    @browsing
    def test_invoking_accept_remote_task_requires_add_portal_content(self, browser):
        self.login(self.regular_user)
        url = '{}/@accept-remote-task'.format(self.dossier.absolute_url())
        self.logout()

        # Merely invoking the endpoint requires Add Portal Content.
        # The required permission checks on the remote side will then
        # be performed as usual, the endpoint just proxies the request
        # in the security context of the user.
        with browser.expect_http_error(code=401):
            browser.open(url, method='POST', headers=self.api_headers)

    @browsing
    def test_requires_task_oguid_parameter(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@accept-remote-task'.format(self.dossier.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Required parameter "task_oguid" is missing in body'},
            browser.json)

    @browsing
    def test_rejects_unexpected_parameters(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@accept-remote-task'.format(self.dossier.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({
                    'task_oguid': 'fa:12345',
                    'unexpected': 'garbage',
                }),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Unexpected parameter(s) in JSON body: ["unexpected"]. '
                         u'Supported parameters are: ["task_oguid", "text"]'},
            browser.json)

    @browsing
    def test_requires_valid_task_oguid(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@accept-remote-task'.format(self.dossier.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'task_oguid': 'i_am_malformed'}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'MalformedOguid: i_am_malformed'},
            browser.json)

    @browsing
    def test_requires_oguid_that_refers_to_remote_object(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@accept-remote-task'.format(self.dossier.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'task_oguid': 'plone:1234'}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Task must be on remote admin unit. '
                         u'Oguid plone:1234 refers to a local task, however.'},
            browser.json)

    @browsing
    @skip('issuer/responsible field titles should contain username, not userid')
    def test_accept_remote_task_creates_successor(self, browser):
        self.login(self.regular_user, browser)

        predecessor = create(
            Builder('task')
            .within(self.dossier)
            .having(issuer=self.dossier_responsible.id,
                    responsible=self.regular_user.id,
                    responsible_client='fa',
                    task_type='correction')
            .in_state('task-state-open')
            .titled(u'Task x'))

        doc_in_task = create(Builder('document')
                             .within(predecessor)
                             .titled(u'Feedback zum Vertragsentwurf')
                             .attach_file_containing(
                                 'Feedback text',
                                 u'vertr\xe4g sentwurf.docx'))

        sql_task = predecessor.get_sql_object()

        local_url = '/'.join((self.dossier.absolute_url(), '@accept-remote-task'))

        # Need to trick @accept-remote-task into thinking it's a remote task
        # so that the corresponding check can be bypassed.
        #
        # Any further remote / local distinction then is handled by
        # dispatch_request(), which will just dispatch these requests
        # internally using restrictedTraverse, but otherwise the
        # transporting / serialization aspects behave largely the same and
        # still get exercised.
        with patch('opengever.api.accept_remote_task.'
                   'AcceptRemoteTaskPost.is_remote') as mock_is_remote:
            mock_is_remote.return_value = True

            request_body = json.dumps({
                'task_oguid': u'plone:%s' % sql_task.int_id,
                'text': u'I hereby accept this task.',
            })

            browser.open(
                local_url, method='POST',
                data=request_body,
                headers=self.api_headers)

        response = browser.json
        successor = Oguid.parse(response['oguid']).resolve_object()

        # Predecessor should be accepted
        self.assertEqual(
            'task-state-in-progress',
            api.content.get_state(predecessor))

        # Successor should also be accepted
        self.assertEqual('task-state-in-progress', api.content.get_state(successor))
        self.assertEqual(u'task-state-in-progress', response['review_state'])

        # Successor should be linked to predecessor
        self.assertEqual(str(predecessor.oguid), successor.predecessor)

        # Response text should be on both successor and predecessor
        self.assertEqual(
            u'I hereby accept this task.',
            self.last_response(predecessor).text)
        self.assertEqual(
            u'I hereby accept this task.',
            self.last_response(successor).text)

        # Responsible should match the responsible of the predecessor
        self.assertEqual(predecessor.responsible, successor.responsible)
        self.assertDictContainsSubset(
            {u'token': u'fa:%s' % self.regular_user.id},
            response['responsible'])

        # Documents should have been copied
        self.assertEqual(1, len(successor.objectIds()))
        self.assertEqual(1, len(response['items']))

        doc_in_successor_task = successor.objectValues()[0]
        self.assertEqual(doc_in_task.title, doc_in_successor_task.title)

        # Response body should contain serialized successor task, including
        # responses and copied documents
        self.assertDictContainsSubset({
            u'@id': successor.absolute_url(),
            u'@type': u'opengever.task.task',
            u'UID': successor.UID(),
            u'issuer': {u'title': u'Ziegler Robert (%s)' % self.dossier_responsible.getUserName(),
                        u'token': self.dossier_responsible.id},
            u'oguid': str(successor.oguid),
            u'predecessor': str(predecessor.oguid),
            u'responsible': {u'title': u'Finanz\xe4mt: B\xe4rfuss K\xe4thi (%s)' % self.regular_user.getUserName(),
                             u'token': u'fa:%s' % self.regular_user.id},
            u'responsible_client': {u'title': u'Finanz\xe4mt',
                                    u'token': u'fa'},
            u'review_state': u'task-state-in-progress',
            u'revoke_permissions': True,
            u'task_type': {u'title': u'For your review',
                           u'token': u'correction'},
            u'title': u'Task x'},
            browser.json)

        self.assertEqual([{
            u'@id': doc_in_successor_task.absolute_url(),
            u'@type': u'opengever.document.document',
            u'UID': doc_in_successor_task.UID(),
            u'description': u'',
            u'checked_out': u'',
            u'file_extension': u'.docx',
            u'is_leafnode': None,
            u'review_state': u'document-state-draft',
            u'title': doc_in_successor_task.title}],
            response['items'])

        self.assertDictContainsSubset({
            u'added_objects': [],
            u'changes': [],
            u'creator': {u'title': u'B\xe4rfuss K\xe4thi',
                         u'token': self.regular_user.id},
            u'mimetype': u'',
            u'related_items': [],
            u'rendered_text': u'',
            u'response_type': u'default',
            u'successor_oguid': u'',
            u'text': u'I hereby accept this task.',
            u'transition': u'task-transition-open-in-progress'},
            response['responses'][-1])
