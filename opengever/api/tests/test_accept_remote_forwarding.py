from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from mock import patch
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseContainer
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestAcceptRemoteForwardingPost(IntegrationTestCase):

    def last_response(self, obj):
        return IResponseContainer(obj).list()[-1]

    @browsing
    def test_requires_forwarding_oguid_parameter(self, browser):
        self.login(self.secretariat_user, browser)
        url = '{}/@accept-remote-forwarding'.format(self.inbox.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Required parameter "forwarding_oguid" is missing in body'},
            browser.json)

    @browsing
    def test_rejects_unexpected_parameters(self, browser):
        self.login(self.secretariat_user, browser)
        url = '{}/@accept-remote-forwarding'.format(self.inbox.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({
                    'forwarding_oguid': 'fa:12345',
                    'unexpected': 'garbage',
                }),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Unexpected parameter(s) in JSON body: ["unexpected"]. '
                         u'Supported parameters are: ["forwarding_oguid", "dossier_oguid", "text"]'},
            browser.json)

    @browsing
    def test_malformed_forwarding_oguid_raises_bad_reqest(self, browser):
        self.login(self.secretariat_user, browser)
        url = '{}/@accept-remote-forwarding'.format(self.inbox.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'forwarding_oguid': 'i_am_malformed'}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'MalformedOguid: i_am_malformed'},
            browser.json)

    @browsing
    def test_invalid_forwarding_oguid_raises_bad_reqest(self, browser):
        self.login(self.secretariat_user, browser)
        url = '{}/@accept-remote-forwarding'.format(self.inbox.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'forwarding_oguid': 'fd:101010'}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'No object found for forwarding_oguid "fd:101010".'},
            browser.json)

    @browsing
    def test_forwarding_not_assigned_to_current_admin_unit_raises_bad_request(self, browser):
        self.login(self.secretariat_user, browser)
        url = '{}/@accept-remote-forwarding'.format(self.inbox.absolute_url())

        with patch('opengever.api.accept_remote_forwarding.'
                   'AcceptRemoteForwardingPost.is_assigned_to_current_admin_unit') as mock_is_remote:
            mock_is_remote.return_value = False

            with browser.expect_http_error(code=400):
                browser.open(
                    url, method='POST',
                    data=json.dumps({'forwarding_oguid': Oguid.for_object(self.inbox_forwarding).id}),
                    headers=self.api_headers)

            self.assertEqual(
                {u'type': u'BadRequest',
                 u'message': u'Forwarding must be assigned to the current admin unit.'},
                browser.json)

    @browsing
    def test_requires_forwarding_oguid_that_refers_to_remote_object(self, browser):
        self.login(self.secretariat_user, browser)
        url = '{}/@accept-remote-forwarding'.format(self.inbox.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'forwarding_oguid': Oguid.for_object(self.inbox_forwarding).id}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Forwarding must be on remote admin unit. Oguid {} refers to a local task,'
                         u' however.'.format(Oguid.for_object(self.inbox_forwarding).id)},
            browser.json)

    @browsing
    def test_malformed_dossier_oguid_raises_bad_reqest(self, browser):
        self.login(self.secretariat_user, browser)
        url = '{}/@accept-remote-forwarding'.format(self.inbox.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'forwarding_oguid': Oguid.for_object(self.inbox_forwarding).id,
                                 'dossier_oguid': 'i_am_malformed'}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'MalformedOguid: i_am_malformed'},
            browser.json)

    @browsing
    def test_invalid_dossier_oguid_raises_bad_reqest(self, browser):
        self.login(self.secretariat_user, browser)
        url = '{}/@accept-remote-forwarding'.format(self.inbox.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(
                url, method='POST',
                data=json.dumps({'forwarding_oguid': Oguid.for_object(self.inbox_forwarding).id,
                                 'dossier_oguid': 'fd:101010'}),
                headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'No object found for dossier_oguid "fd:101010".'},
            browser.json)

    @browsing
    def test_accept_remote_forwarding_creates_successor(self, browser):
        self.login(self.secretariat_user, browser)

        forwarding = create(Builder('forwarding')
                            .within(self.inbox_rk)
                            .titled(u'F\xf6rw\xe4rding')
                            .having(responsible_client='fa',
                                    responsible='inbox:fa',
                                    issuer='inbox:rk'))

        doc_in_forwarding = create(Builder('document').within(forwarding)
                                   .titled(u'Dokument im Eingangsk\xf6rbliweiterleitung')
                                   .with_asset_file('text.txt'))

        sql_forwarding = forwarding.get_sql_object()

        local_url = '/'.join((self.inbox.absolute_url(), '@accept-remote-forwarding'))

        # Need to trick @accept-remote-forwarding into thinking it's a remote forwarding
        # so that the corresponding check can be bypassed.
        #
        # Any further remote / local distinction then is handled by
        # dispatch_request(), which will just dispatch these requests
        # internally using restrictedTraverse, but otherwise the
        # transporting / serialization aspects behave largely the same and
        # still get exercised.
        with patch('opengever.api.accept_remote_forwarding.'
                   'AcceptRemoteForwardingPost.is_remote') as mock_is_remote:
            mock_is_remote.return_value = True

            request_body = json.dumps({
                'forwarding_oguid': u'plone:%s' % sql_forwarding.int_id,
                'text': u'I hereby accept this forwarding.',
            })

            browser.open(local_url, method='POST', data=request_body, headers=self.api_headers)

        response = browser.json
        successor = Oguid.parse(response['oguid']).resolve_object()

        # Successor should be in inbox
        self.assertEqual('opengever.inbox.inbox', successor.aq_parent.portal_type)

        # Forwarding should be closed
        self.assertEqual(
            'forwarding-state-closed',
            api.content.get_state(forwarding))

        # Successor should also be accepted
        self.assertEqual('forwarding-state-open', api.content.get_state(successor))

        # Successor should be linked to predecessor
        self.assertEqual(str(forwarding.oguid), successor.predecessor)

        # Responsible should match the responsible of the predecessor
        self.assertEqual(forwarding.responsible, successor.responsible)

        # Documents should have been copied
        self.assertEqual(1, len(successor.objectIds()))
        self.assertEqual(1, len(response['items']))

        doc_in_successor_forwarding = successor.objectValues()[0]
        self.assertEqual(doc_in_forwarding.title, doc_in_successor_forwarding.title)

        # Response body should contain serialized successor forwarding, including
        # responses and copied documents
        self.assertDictContainsSubset({
            u'@id': successor.absolute_url(),
            u'@type': u'opengever.inbox.forwarding',
            u'UID': successor.UID(),
            u'issuer': {u'token': u'inbox:fa', u'title': u'Inbox: Finanz\xe4mt'},
            u'oguid': str(successor.oguid),
            u'predecessor': str(forwarding.oguid),
            u'responsible': {u'token': u'inbox:fa', u'title': u'Inbox: Finanz\xe4mt'},
            u'responsible_client': {u'token': u'fa', u'title': u'Finanz\xe4mt'},
            u'review_state': u'forwarding-state-open',
            u'task_type': {u'token': u'forwarding_task_type', u'title': u'Forwarding'},
            u'title': u'F\xf6rw\xe4rding'},
            browser.json)

        self.assertEqual([{
            u'@id': doc_in_successor_forwarding.absolute_url(),
            u'@type': u'opengever.document.document',
            u'UID': doc_in_successor_forwarding.UID(),
            u'description': u'',
            u'checked_out': u'',
            u'file_extension': u'.txt',
            u'is_leafnode': None,
            u'review_state': u'document-state-draft',
            u'title': doc_in_successor_forwarding.title}],
            response['items'])

    def _accept_remote_forwarding_creates_task_in_dossier(self, browser, response):
        self.login(self.secretariat_user, browser)

        forwarding = create(Builder('forwarding')
                            .within(self.inbox_rk)
                            .titled(u'F\xf6rw\xe4rding')
                            .having(responsible_client='fa',
                                    responsible='inbox:fa',
                                    issuer='inbox:rk'))

        doc_in_forwarding = create(Builder('document').within(forwarding)
                                   .titled(u'Dokument im Eingangsk\xf6rbliweiterleitung')
                                   .with_asset_file('text.txt'))

        sql_forwarding = forwarding.get_sql_object()

        local_url = '/'.join((self.inbox.absolute_url(), '@accept-remote-forwarding'))

        # Need to trick @accept-remote-forwarding into thinking it's a remote forwarding
        # so that the corresponding check can be bypassed.
        #
        # Any further remote / local distinction then is handled by
        # dispatch_request(), which will just dispatch these requests
        # internally using restrictedTraverse, but otherwise the
        # transporting / serialization aspects behave largely the same and
        # still get exercised.
        with patch('opengever.api.accept_remote_forwarding.'
                   'AcceptRemoteForwardingPost.is_remote') as mock_is_remote:
            mock_is_remote.return_value = True

            request_body = json.dumps({
                'dossier_oguid': Oguid.for_object(self.dossier).id,
                'forwarding_oguid': u'plone:%s' % sql_forwarding.int_id,
                'text': response,
            })

            browser.open(local_url, method='POST', data=request_body, headers=self.api_headers)

        response = browser.json
        task = Oguid.parse(response['oguid']).resolve_object()
        successor = Oguid.parse(task.predecessor).resolve_object()

        # Successor should be in yearfolder
        self.assertEqual('opengever.inbox.yearfolder', successor.aq_parent.portal_type)

        # Predecessor and successor should be closed
        self.assertEqual('forwarding-state-closed', api.content.get_state(forwarding))
        self.assertEqual('forwarding-state-closed', api.content.get_state(successor))

        # Task should alse be accepted
        self.assertEqual('task-state-open', api.content.get_state(task))

        # Successor should be linked to predecessor
        self.assertEqual(str(forwarding.oguid), successor.predecessor)
        self.assertEqual(str(successor.oguid), task.predecessor)

        # Responsible should match the responsible of the predecessor
        self.assertEqual(forwarding.responsible, successor.responsible)
        self.assertEqual(forwarding.responsible, task.responsible)

        # Documents should have been copied
        self.assertEqual(1, len(successor.objectIds()))
        self.assertEqual(1, len(task.objectIds()))
        self.assertEqual(1, len(response['items']))

        doc_in_task = task.objectValues()[0]
        self.assertEqual(doc_in_forwarding.title, doc_in_task.title)

        # Response body should contain serialized task, including
        # responses and copied documents
        self.assertDictContainsSubset({
            u'@id': task.absolute_url(),
            u'@type': u'opengever.task.task',
            u'UID': task.UID(),
            u'issuer': {u'token': u'inbox:fa', u'title': u'Inbox: Finanz\xe4mt'},
            u'oguid': str(task.oguid),
            u'predecessor': str(successor.oguid),
            u'responsible': {u'token': u'inbox:fa', u'title': u'Inbox: Finanz\xe4mt'},
            u'responsible_client': {u'token': u'fa', u'title': u'Finanz\xe4mt'},
            u'review_state': u'task-state-open',
            u'task_type': {u'title': u'For your information', u'token': u'information'},
            u'title': u'F\xf6rw\xe4rding'},
            browser.json)

        self.assertEqual([{
            u'@id': doc_in_task.absolute_url(),
            u'@type': u'opengever.document.document',
            u'UID': doc_in_task.UID(),
            u'description': u'',
            u'checked_out': u'',
            u'file_extension': u'.txt',
            u'is_leafnode': None,
            u'review_state': u'document-state-draft',
            u'title': doc_in_task.title}],
            response['items'])

        self.assertEqual(self.dossier.absolute_url(), response['parent']['@id'])

    @browsing
    def test_accept_remote_forwarding_with_response_creates_task_in_dossier(self, browser):
        self._accept_remote_forwarding_creates_task_in_dossier(
            browser, response=u'I hereby accept this forwarding.')

    @browsing
    def test_accept_remote_forwarding_without_response_creates_task_in_dossier(self, browser):
        self._accept_remote_forwarding_creates_task_in_dossier(
            browser, response=None)
