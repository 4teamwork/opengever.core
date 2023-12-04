from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.mail.tests import MAIL_DATA
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher
from unittest import skip
import json


class TestWorkflowPost(IntegrationTestCase):

    @browsing
    def test_transition_reassigning_task_and_revoking_users_permissions_can_be_executed(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {
            'responsible': {
                'token': 'rk:{}'.format(self.dossier_responsible.getId())
            }
        }
        # this reassigns the task so that `regular_user` no longer has access
        browser.open(
            self.task_in_protected_dossier.absolute_url() + '/@workflow/task-transition-reassign',
            json.dumps(data), method='POST', headers=self.api_headers
        )

        self.assertDictContainsSubset(
            {u'title': u'In progress',
             u'actor': self.regular_user.id,
             u'action': u'task-transition-reassign',
             u'review_state': u'task-state-in-progress'},
            browser.json
        )

    @browsing
    def test_transition_close_task_and_revoking_users_permissions_can_be_executed(self, browser):
        self.login(self.regular_user, browser=browser)

        # only direct execution tasks can be closed directly
        self.task_in_protected_dossier.task_type = 'direct-execution'

        # this closes the task so that `regular_user` no longer has access
        browser.open(
            self.task_in_protected_dossier.absolute_url() + '/@workflow/task-transition-in-progress-tested-and-closed',
            method='POST', headers=self.api_headers
        )

        self.assertDictContainsSubset(
            {u'title': u'Closed',
             u'actor': self.regular_user.id,
             u'action': u'task-transition-in-progress-tested-and-closed',
             u'review_state': u'task-state-tested-and-closed'},
            browser.json
        )

    @browsing
    @skip('This test fails for yet unknown reasons after changing the userid of kathi.barfuss to regular_user')
    def test_transition_remove_document_and_revoking_users_permission_can_be_executed(self, browser):
        self.login(self.manager)
        # allow `regular_user` to remove gever content
        self.portal.manage_permission(
            'Remove GEVER content', roles=['Editor'], acquire=True)

        self.login(self.regular_user, browser=browser)
        ITrasher(self.document).trash()
        # this soft-deletes the document so that `regular_user` no longer has
        # access
        browser.open(
            self.document.absolute_url() + '/@workflow/document-transition-remove',
            method='POST', headers=self.api_headers)

        self.assertDictContainsSubset(
            {u'title': u'Removed',
             u'actor': self.regular_user.id,
             u'action': u'document-transition-remove',
             u'review_state': u'document-state-removed'},
            browser.json
        )

    @browsing
    def test_transition_remove_document_can_be_executed(self, browser):
        self.login(self.manager)
        # allow `secretariat_user` to remove gever content
        self.portal.manage_permission(
            'Remove GEVER content', roles=['Editor'], acquire=True)

        self.login(self.secretariat_user, browser=browser)
        ITrasher(self.inbox_document).trash()

        browser.open(
            self.inbox_document.absolute_url() + '/@workflow/document-transition-remove',
            method='POST', headers=self.api_headers)

        self.assertDictContainsSubset(
            {u'title': u'Removed',
             u'actor': self.secretariat_user.id,
             u'action': u'document-transition-remove',
             u'review_state': u'document-state-removed'},
            browser.json
        )

    @browsing
    def test_transition_remove_mail_can_be_executed(self, browser):
        self.login(self.manager)
        # allow `secretariat_user` to remove gever content
        self.portal.manage_permission(
            'Remove GEVER content', roles=['Editor'], acquire=True)

        mail = create(
            Builder("mail")
            .with_message(MAIL_DATA)
            .within(self.inbox)
        )
        self.login(self.secretariat_user, browser=browser)
        ITrasher(mail).trash()

        browser.open(
            mail.absolute_url() + '/@workflow/mail-transition-remove',
            method='POST', headers=self.api_headers)

        self.assertDictEqual(
            {u'review_state': u'mail-state-removed',
             u'title': u'mail-state-removed'},
            browser.json)

    @browsing
    def test_calling_endpoint_without_transition_gives_400(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=400):
            browser.open(
                self.dossier.absolute_url() + '/@workflow',
                method='POST', headers=self.api_headers)

        self.assertEqual('Bad Request', browser.json['error']['type'])
        self.assertIn(u"Invalid transition 'None'",
                      browser.json['error']['message'])

    @browsing
    def test_calling_workflow_with_additional_path_segments_results_in_404(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=404):
            browser.open(
                self.dossier.absolute_url() + '/@workflow/dossier-transition-resolve/invalid',
                method='POST', headers=self.api_headers)

        self.assertEqual('NotFound', browser.json['type'])

    @browsing
    def test_invalid_transition_results_in_400(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=400):
            browser.open(
                self.dossier.absolute_url() + '/@workflow/invalid-transition',
                method='POST', headers=self.api_headers)

        self.assertEqual('Bad Request', browser.json['error']['type'])
        self.assertIn(u"Invalid transition 'invalid-transition'",
                      browser.json['error']['message'])


class TestWorkflowSchemaEndpoint(IntegrationTestCase):

    features = ('filing_number', )

    @browsing
    def test_raise_if_transition_is_not_given(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=400):
            browser.open(self.empty_dossier, method="GET",
                         headers=self.api_headers,
                         view='@workflow-schema')

        self.assertEqual(
            {u'error': {
                u'message': u'Missing transition',
                u'type': u'BadRequest'}},
            browser.json)

    @browsing
    def test_return_serialized_schema(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.empty_dossier, method="GET",
                     headers=self.api_headers,
                     view='@workflow-schema/dossier-transition-resolve')

        self.assertEqual([u'required', u'properties', u'fieldsets'],
                         browser.json.keys())

        self.assertEqual(
            [{u'fields': [u'filing_prefix', u'dossier_enddate',
                          u'filing_year', u'filing_action'],
              u'id': u'default',
              u'behavior': u'plone',
              u'title': u'Default'}],
            browser.json['fieldsets'])

        self.assertEqual(
            {
                u'dossier_enddate': {
                    u'widget': u'date',
                    u'description': u'',
                    u'title': u'End date',
                    u'default': u'2016-01-01',
                    u'factory': u'Date',
                    u'type': u'string'},
                u'filing_action': {
                    u'description': u'',
                    u'vocabulary': {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-7/@vocabularies/filing_action'},
                    u'title': u'Action',
                    u'enum': [u'resolve and set filing no',
                              u'only resolve, set filing no later'],
                    u'factory': u'Choice',
                    u'choices': [
                        [u'resolve and set filing no',
                         u'Resolve and issue filing number'],
                        [u'only resolve, set filing no later',
                         u"Just resolve, don't issue a filing number yet"]],
                    u'enumNames': [
                        u'Resolve and issue filing number',
                        u"Just resolve, don't issue a filing number yet"],
                    u'type': u'string'},
                u'filing_year': {
                    u'default': u'2016',
                    u'title': u'Filing year',
                    u'type': u'string',
                    u'description': u'',
                    u'factory': u'Text line (String)'},
                u'filing_prefix': {
                    u'description': u'',
                    u'vocabulary': {
                        u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-7/@sources/filing_prefix'},
                    u'title': u'Filing number prefix',
                    u'enum': [
                        u'administration',
                        u'government',
                        u'department',
                        u'directorate',
                        u'personal'],
                    u'factory': u'Choice',
                    u'choices': [
                        [u'administration', u'Administration'],
                        [u'government', u'Cantonal Government'],
                        [u'department', u'Department'],
                        [u'directorate', u'Directorate'],
                        [u'personal', u'Human Resources']],
                    u'enumNames': [
                        u'Administration',
                        u'Cantonal Government',
                        u'Department',
                        u'Directorate',
                        u'Human Resources'],
                    u'type': u'string'}
            },
            browser.json['properties'])

        self.assertEqual([u'dossier_enddate', u'filing_action'],
                         browser.json['required'])

    @browsing
    def test_returns_empty_configuration_when_no_schemas_are_registered(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.empty_dossier, method="GET",
                     headers=self.api_headers,
                     view='@workflow-schema/dossier-transition-deactivate')

        self.assertEqual({"properties": {}, "required": [], "fieldsets": []},
                         browser.json)
