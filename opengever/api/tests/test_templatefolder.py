from datetime import date
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest
import json


class TestDocumentFromTemplatePost(IntegrationTestCase):

    @browsing
    def test_creates_document_from_template(self, browser):
        self.login(self.regular_user, browser)

        browser.open(
            '{}/@vocabularies/opengever.dossier.DocumentTemplatesVocabulary'.format(
                self.portal.absolute_url()),
            headers=self.api_headers)
        template = browser.json['items'][0]

        data = {'template': template,
                'title': u'New d\xf6cument'}

        with self.observe_children(self.dossier) as children:
            browser.open('{}/@document-from-template'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        document = children['added'].pop()

        self.assertEqual(u'New d\xf6cument', document.title)
        self.assertEquals(date.today(), document.document_date)

    @browsing
    def test_requires_title(self, browser):
        self.login(self.regular_user, browser)

        browser.open(
            '{}/@vocabularies/opengever.dossier.DocumentTemplatesVocabulary'.format(
                self.portal.absolute_url()),
            headers=self.api_headers)
        template = browser.json['items'][0]

        data = {'template': template}

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as exc:
            browser.open('{}/@document-from-template'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual('Missing parameter title', str(exc.exception))

    @browsing
    def test_requires_template(self, browser):
        self.login(self.regular_user, browser)

        data = {'title': u'New d\xf6cument'}

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as exc:
            browser.open('{}/@document-from-template'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual('Missing parameter template', str(exc.exception))

    @browsing
    def test_requires_add_permission(self, browser):
        with self.login(self.regular_user):
            RoleAssignmentManager(self.portal).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )
            RoleAssignmentManager(self.dossier).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )

        self.login(self.reader_user, browser)
        data = {'template': {'token': '1234567890'},
                'title': u'New d\xf6cument'}

        with browser.expect_unauthorized():
            browser.open('{}/@document-from-template'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)
