from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from mock import patch
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseContainer
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestCloseRemoteTaskPost(IntegrationTestCase):

    def last_response(self, obj):
        return IResponseContainer(obj).list()[-1]

    @browsing
    def test_requires_task_oguid_parameter(self, browser):
        self.login(self.regular_user, browser)
        url = '{}/@close-remote-task'.format(self.portal.absolute_url())

        with browser.expect_http_error(code=400):
            browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'Required parameter "task_oguid" is missing in body'},
            browser.json)

    @browsing
    def test_requires_dossier_uid_when_documents_are_selected(self, browser):
        self.login(self.regular_user, browser)

        task = create(Builder('task')
                      .within(self.dossier)
                      .having(issuer=self.dossier_responsible.id,
                              responsible=self.regular_user.id,
                              responsible_client='fa',
                              task_type='information')
                      .relate_to([self.document, self.mail_eml])
                      .in_state('task-state-open')
                      .titled(u'Task x'))

        url = '{}/@close-remote-task'.format(self.portal.absolute_url())
        request_body = json.dumps({
            'task_oguid': u'plone:%s' % task.get_sql_object().int_id,
            'text': u'All right!',
            'document_oguids': [Oguid.for_object(self.document).id],
        })

        with browser.expect_http_error(code=400):
            browser.open(url, method='POST', data=request_body, headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'message': u'dossier_uid is required when selecting documents for copying.'},
            browser.json)

    @browsing
    def test_closes_and_copy_documents_successfull(self, browser):
        self.login(self.regular_user, browser)

        task = create(Builder('task')
                      .within(self.dossier)
                      .having(issuer=self.dossier_responsible.id,
                              responsible=self.regular_user.id,
                              responsible_client='fa',
                              task_type='information')
                      .relate_to([self.document, self.mail_eml])
                      .in_state('task-state-open')
                      .titled(u'Task x'))

        url = '{}/@close-remote-task'.format(self.portal.absolute_url())
        request_body = json.dumps({
            'task_oguid': Oguid.for_object(task).id,
            'dossier_uid': self.empty_dossier.UID(),
            'text': u'All right!',
            'document_oguids': [Oguid.for_object(self.document).id],
        })

        with self.observe_children(self.empty_dossier) as children:
            with patch('opengever.api.close_remote_task.'
                       'CloseRemoteTaskPost.is_remote') as mock_is_remote:
                mock_is_remote.return_value = True
                browser.open(url, method='POST', data=request_body,
                             headers=self.api_headers)

        doc, = children['added']
        self.assertEqual(self.document.title, doc.title)
        self.assertEqual(self.document.file.data, doc.file.data)

        self.assertEqual('task-state-tested-and-closed',
                         api.content.get_state(task))
