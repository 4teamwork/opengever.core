from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestMove(IntegrationTestCase):

    def setUp(self):
        super(TestMove, self).setUp()

    @browsing
    def test_regular_user_can_move_document(self, browser):
        self.login(self.regular_user, browser)
        doc_id = self.document.getId()
        browser.open(
            self.subdossier.absolute_url() + '/@move',
            data=json.dumps({"source": self.document.absolute_url()}),
            method='POST',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'},
        )
        self.assertEqual(200, browser.status_code)
        self.assertIn(doc_id, self.subdossier)

    @browsing
    def test_move_document_within_templatefolder_is_possible(self, browser):
        self.login(self.administrator, browser)
        doc_id = self.dossiertemplatedocument.getId()
        browser.open(
            self.templates, view='@move',
            data=json.dumps({"source": self.dossiertemplatedocument.absolute_url()}),
            method='POST', headers=self.api_headers,
        )
        self.assertEqual(200, browser.status_code)
        self.assertIn(doc_id, self.templates)

    @browsing
    def test_document_within_repository_cannot_be_moved_to_templates(self, browser):
        self.login(self.administrator, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.templates, view='/@move',
                         data=json.dumps({"source": self.document.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_docs_cant_be_moved_from_repo_to_templates',
             u'translated_message': u'Documents within the repository cannot be moved to the templates.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_document_within_inbox_cannot_be_moved_to_templates(self, browser):
        self.login(self.administrator, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.templates, view='/@move',
                         data=json.dumps({"source": self.inbox_document.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_docs_cant_be_moved_from_inbox_to_templates',
             u'translated_message': u'Documents within the inbox cannot be moved to the templates.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_move_document_within_private_folder_is_possible(self, browser):
        self.login(self.regular_user, browser)
        dossier = create(
            Builder('private_dossier')
            .within(self.private_folder))

        doc_id = self.private_document.getId()

        browser.open(
            dossier, view='@move',
            data=json.dumps({"source": self.private_document.absolute_url()}),
            method='POST', headers=self.api_headers,
        )
        self.assertEqual(200, browser.status_code)
        self.assertIn(doc_id, dossier)

    @browsing
    def test_document_within_repository_cannot_be_moved_to_private_dossier(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.private_dossier, view='/@move',
                         data=json.dumps({"source": self.document.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_docs_cant_be_moved_from_repo_to_private_repo',
             u'translated_message': u'Documents within the repository cannot be moved to the private repository.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_document_within_inbox_cannot_be_moved_to_private_dossier(self, browser):
        self.login(self.secretariat_user, browser)
        private_folder = create(
            Builder('private_folder')
            .having(id=self.secretariat_user.getId())
            .within(self.private_root)
        )

        private_dossier = create(
            Builder('private_dossier')
            .having(title=u'Mein Dossier 1')
            .within(private_folder)
        )

        with browser.expect_http_error(code=403):
            browser.open(private_dossier, view='/@move',
                         data=json.dumps({"source": self.inbox_document.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_docs_cant_be_moved_from_inbox_to_private_repo',
             u'translated_message': u'Documents within the inbox cannot be moved to the private repository.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_document_inside_a_task_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.dossier, view='/@move',
                         data=json.dumps({"source": self.taskdocument.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_doc_inside_task_cant_be_moved',
             u'translated_message': u'Documents inside a task cannot be moved.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_mail_inside_a_task_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail').titled('Good news').within(self.task))

        with browser.expect_http_error(code=403):
            browser.open(self.dossier, view='/@move',
                         data=json.dumps({"source": mail.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_doc_inside_task_cant_be_moved',
             u'translated_message': u'Documents inside a task cannot be moved.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_document_inside_a_proposal_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.dossier, view='/@move',
                         data=json.dumps({"source": self.proposaldocument.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_doc_inside_proposal_cant_be_moved',
             u'translated_message': u'Documents inside a proposal cannot be moved.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_mail_inside_a_proposal_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail').titled('Good news').within(self.proposal))

        with browser.expect_http_error(code=403):
            browser.open(self.dossier, view='/@move',
                         data=json.dumps({"source": mail.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_doc_inside_proposal_cant_be_moved',
             u'translated_message': u'Documents inside a proposal cannot be moved.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_document_inside_a_closed_dossier_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.dossier, view='/@move',
                         data=json.dumps({"source": self.expired_document.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_doc_inside_closed_dossier',
             u'translated_message': u'Documents inside a closed dossier cannot be moved.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_mail_inside_a_closed_dossier_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        with browser.expect_http_error(code=403):
            browser.open(self.empty_dossier, view='/@move',
                         data=json.dumps({"source": self.mail_eml.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_doc_inside_closed_dossier',
             u'translated_message': u'Documents inside a closed dossier cannot be moved.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_moving_dossier_respects_maximum_dossier_depth(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=403):
            browser.open(self.subdossier, view='/@move',
                         data=json.dumps({"source": self.empty_dossier.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_would_exceed_max_dossier_level',
             u'translated_message': u'This would exceed the maximally allowed dossier depth.',
             u'type': u'Forbidden'},
            browser.json)

        api.portal.set_registry_record(name='maximum_dossier_depth',
                                       value=2,
                                       interface=IDossierContainerTypes)

        empty_dossier_title = self.empty_dossier.Title()
        with self.observe_children(self.subdossier) as children:
            browser.open(self.subdossier, view='/@move',
                         data=json.dumps({"source": self.empty_dossier.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(1, len(children["added"]))
        self.assertEqual(empty_dossier_title, children["added"].pop().Title())

    @browsing
    def test_moving_dossier_with_subdossier_respects_maximum_dossier_depth(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403):
            browser.open(self.empty_dossier, view='/@move',
                         data=json.dumps({"source": self.resolvable_dossier.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_would_exceed_max_dossier_level',
             u'translated_message': u'This would exceed the maximally allowed dossier depth.',
             u'type': u'Forbidden'},
            browser.json)

        api.portal.set_registry_record(name='maximum_dossier_depth',
                                       value=2,
                                       interface=IDossierContainerTypes)

        resolvable_dossier_title = self.resolvable_dossier.Title()
        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, view='/@move',
                         data=json.dumps({"source": self.resolvable_dossier.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(1, len(children["added"]))
        self.assertEqual(resolvable_dossier_title, children["added"].pop().Title())

    @browsing
    def test_moving_object_with_read_permissions_is_forbidden(self, browser):
        self.login(self.manager)

        self.subsubdossier.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.subsubdossier).add_or_update_assignment(
            SharingRoleAssignment(self.regular_user.getId(),
                                  ['Reader', 'Contributor'],
                                  self.subsubdossier))

        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403):
            browser.open(self.empty_dossier, view='/@move',
                         data=json.dumps({"source": self.subsubdossier.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'move_object_disallowed',
             u'translated_message': u'You are not allowed to move this object.',
             u'type': u'Forbidden'},
            browser.json)

        with browser.expect_http_error(code=403):
            browser.open(self.empty_dossier, view='/@move',
                         data=json.dumps({"source": self.subsubdocument.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'move_object_disallowed',
             u'translated_message': u'You are not allowed to move this object.',
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_move_dossiertemplate_to_templatefolder_is_possible(self, browser):
        self.login(self.administrator, browser)
        with self.observe_children(self.subtemplates) as children:
            browser.open(
                self.subtemplates, view='@move',
                data=json.dumps({"source": self.dossiertemplate.absolute_url()}),
                method='POST', headers=self.api_headers,
            )
        self.assertEqual(200, browser.status_code)
        self.assertEqual(1, len(children["added"]))

    @browsing
    def test_moving_dossiertemplate_respects_maximum_dossier_depth_if_flag_enabled(self, browser):
        self.login(self.administrator, browser)
        api.portal.set_registry_record('respect_max_depth', True,
                                       interface=IDossierTemplateSettings)

        empty_dossiertemplate = create(Builder('dossiertemplate')
                                       .within(self.templates))
        with browser.expect_http_error(code=403):
            browser.open(empty_dossiertemplate, view='/@move',
                         data=json.dumps({"source": self.dossiertemplate.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_would_exceed_max_dossier_level',
             u'translated_message': u'This would exceed the maximally allowed dossier depth.',
             u'type': u'Forbidden'},
            browser.json)

        api.portal.set_registry_record('respect_max_depth', False,
                                       interface=IDossierTemplateSettings)

        with self.observe_children(empty_dossiertemplate) as children:
            browser.open(empty_dossiertemplate, view='/@move',
                         data=json.dumps({"source": self.dossiertemplate.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(1, len(children["added"]))

    @browsing
    def test_move_tasktemplatefolder_to_templatefolder_is_possible(self, browser):
        self.login(self.administrator, browser)
        with self.observe_children(self.subtemplates) as children:
            browser.open(
                self.subtemplates, view='@move',
                data=json.dumps({"source": self.tasktemplatefolder.absolute_url()}),
                method='POST', headers=self.api_headers,
            )
        self.assertEqual(200, browser.status_code)
        self.assertEqual(1, len(children["added"]))

    @browsing
    def test_can_only_move_tasktemplatefolder_into_tasktemplatefolder_if_nesting_enabled(self,
                                                                                         browser):
        self.login(self.administrator, browser)
        tasktemplatefolder = create(Builder('tasktemplatefolder').within(self.templates))

        with browser.expect_http_error(code=403):
            browser.open(tasktemplatefolder, view='/@move',
                         data=json.dumps({"source": self.tasktemplatefolder.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u"additional_metadata": {},
             u"message": u"msg_tasktemplatefolder_nesting_not_allowed",
             u"translated_message":
                u"It's not allowed to move tasktemplatefolders into tasktemplatefolders.",
             u"type": u"Forbidden"},
            browser.json)

        self.activate_feature('tasktemplatefolder_nesting')

        with self.observe_children(tasktemplatefolder) as children:
            browser.open(tasktemplatefolder, view='/@move',
                         data=json.dumps({"source": self.tasktemplatefolder.absolute_url()}),
                         method='POST', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(1, len(children["added"]))
