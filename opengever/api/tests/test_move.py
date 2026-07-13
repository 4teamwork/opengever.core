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

    def assert_can_move(self, browser, source, target):
        uid = source.UID()
        with self.observe_children(target) as children:
            browser.open(
                target,
                view='@move',
                data=json.dumps({"source": source.absolute_url()}),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(1, len(children["added"]))
        self.assertEqual(uid, children["added"].pop().UID())

    def assert_cannot_move(self, browser, source, target, message, translated_message):
        with browser.expect_http_error(code=403):
            browser.open(target,
                         view='@move',
                         data=json.dumps({"source": source.absolute_url()}),
                         method='POST',
                         headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': message,
             u'translated_message': translated_message,
             u'type': u'Forbidden'},
            browser.json)

    @browsing
    def test_regular_user_can_move_document(self, browser):
        self.login(self.regular_user, browser)
        self.assert_can_move(browser, self.document, self.subdossier)

    @browsing
    def test_can_move_document_from_teamplatefolder_to_templatefolder(self, browser):
        self.login(self.administrator, browser)
        self.assert_can_move(browser, self.normal_template, self.subtemplates)

    @browsing
    def test_cannot_move_document_from_templates_to_repository(self, browser):
        self.login(self.administrator, browser)
        message = u'msg_docs_cant_be_moved_from_templates_to_repository'
        translated = u'Documents within the templates cannot be moved to the repository.'
        self.assert_cannot_move(
            browser, self.normal_template, self.empty_dossier, message, translated)

        self.assert_cannot_move(
            browser, self.dossiertemplatedocument, self.empty_dossier, message, translated)

    @browsing
    def test_cannot_move_document_from_templates_to_private_repository(self, browser):
        self.login(self.administrator, browser)
        private_folder = create(
            Builder('private_folder')
            .having(id=self.administrator.getId())
            .within(self.private_root)
        )

        private_dossier = create(
            Builder('private_dossier')
            .having(title=u'Mein Dossier 1')
            .within(private_folder)
        )

        message = u'msg_docs_cant_be_moved_from_templates_to_private_repo'
        translated = u'Documents within the templates cannot be moved to the private repository.'
        self.assert_cannot_move(
            browser, self.normal_template, private_dossier, message, translated)

    @browsing
    def test_cannot_move_document_from_teamplatefolder_to_dossier_template(self, browser):
        self.login(self.administrator, browser)
        message = u'msg_docs_cant_be_moved_from_template_folder_to_template_dossier'
        translated = u'Document templates cannot be moved into a dossier template.'
        self.assert_cannot_move(
            browser, self.normal_template, self.dossiertemplate, message, translated)

    @browsing
    def test_cannot_move_document_from_dossier_template_to_teamplatefolder(self, browser):
        self.login(self.administrator, browser)
        message = u'msg_docs_cant_be_moved_from_template_dossier_to_template_folder'
        translated = u'Documents from a dossier template cannot be made into document templates.'
        self.assert_cannot_move(
            browser, self.dossiertemplatedocument, self.templates, message, translated)

    @browsing
    def test_document_within_repository_cannot_be_moved_to_templates(self, browser):
        self.login(self.administrator, browser)
        message = u'msg_docs_cant_be_moved_from_repo_to_templates'
        translated = u'Documents within the repository cannot be moved to the templates.'
        self.assert_cannot_move(
            browser, self.document, self.templates, message, translated)

    @browsing
    def test_document_within_inbox_cannot_be_moved_to_templates(self, browser):
        self.login(self.administrator, browser)

        message = u'msg_docs_cant_be_moved_from_inbox_to_templates'
        translated = u'Documents within the inbox cannot be moved to the templates.'
        self.assert_cannot_move(
            browser, self.inbox_document, self.templates, message, translated)

    @browsing
    def test_move_document_within_private_folder_is_possible(self, browser):
        self.login(self.regular_user, browser)
        dossier = create(
            Builder('private_dossier')
            .within(self.private_folder))

        self.assert_can_move(browser, self.private_document, dossier)

    @browsing
    def test_document_within_repository_cannot_be_moved_to_private_dossier(self, browser):
        self.login(self.regular_user, browser)

        message = u'msg_docs_cant_be_moved_from_repo_to_private_repo'
        translated = u'Documents within the repository cannot be moved to the private repository.'
        self.assert_cannot_move(
            browser, self.document, self.private_dossier, message, translated)

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

        message = u'msg_docs_cant_be_moved_from_inbox_to_private_repo'
        translated = u'Documents within the inbox cannot be moved to the private repository.'
        self.assert_cannot_move(
            browser, self.inbox_document, private_dossier, message, translated)

    @browsing
    def test_document_inside_a_task_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)

        message = u'msg_doc_inside_task_cant_be_moved'
        translated = u'Documents inside a task cannot be moved.'
        self.assert_cannot_move(
            browser, self.taskdocument, self.dossier, message, translated)

    @browsing
    def test_mail_inside_a_task_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail').titled('Good news').within(self.task))

        message = u'msg_doc_inside_task_cant_be_moved'
        translated = u'Documents inside a task cannot be moved.'
        self.assert_cannot_move(
            browser, mail, self.dossier, message, translated)

    @browsing
    def test_document_inside_a_proposal_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)

        message = u'msg_doc_inside_proposal_cant_be_moved'
        translated = u'Documents inside a proposal cannot be moved.'
        self.assert_cannot_move(
            browser, self.proposaldocument, self.dossier, message, translated)

    @browsing
    def test_mail_inside_a_proposal_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail').titled('Good news').within(self.proposal))

        message = u'msg_doc_inside_proposal_cant_be_moved'
        translated = u'Documents inside a proposal cannot be moved.'
        self.assert_cannot_move(
            browser, mail, self.dossier, message, translated)

    @browsing
    def test_document_inside_a_closed_dossier_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)

        message = u'msg_doc_inside_closed_dossier'
        translated = u'Documents inside a closed dossier cannot be moved.'
        self.assert_cannot_move(
            browser, self.expired_document, self.dossier, message, translated)

    @browsing
    def test_mail_inside_a_closed_dossier_cannot_be_moved(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        message = u'msg_doc_inside_closed_dossier'
        translated = u'Documents inside a closed dossier cannot be moved.'
        self.assert_cannot_move(
            browser, self.mail_eml, self.empty_dossier, message, translated)

    @browsing
    def test_moving_dossier_respects_maximum_dossier_depth(self, browser):
        self.login(self.regular_user, browser)

        message = u'msg_would_exceed_max_dossier_level'
        translated = u'This would exceed the maximally allowed dossier depth.'
        self.assert_cannot_move(
            browser, self.empty_dossier, self.subsubdossier, message, translated)

        api.portal.set_registry_record(name='maximum_dossier_depth',
                                       value=3,
                                       interface=IDossierContainerTypes)

        self.assert_can_move(browser, self.empty_dossier, self.subsubdossier)

    @browsing
    def test_moving_dossier_with_subdossier_respects_maximum_dossier_depth(self, browser):
        self.login(self.regular_user, browser)

        message = u'msg_would_exceed_max_dossier_level'
        translated = u'This would exceed the maximally allowed dossier depth.'
        self.assert_cannot_move(
            browser, self.resolvable_dossier, self.empty_dossier, message, translated)

        api.portal.set_registry_record(name='maximum_dossier_depth',
                                       value=2,
                                       interface=IDossierContainerTypes)

        self.assert_can_move(browser, self.resolvable_dossier, self.empty_dossier)

    @browsing
    def test_moving_object_with_read_permissions_is_forbidden(self, browser):
        self.login(self.manager)

        self.subsubdossier.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.subsubdossier).add_or_update_assignment(
            SharingRoleAssignment(self.regular_user.getId(),
                                  ['Reader', 'Contributor'],
                                  self.subsubdossier))

        self.login(self.regular_user, browser)
        message = u'move_object_disallowed'
        translated = u'You are not allowed to move this object.'

        self.assert_cannot_move(
            browser, self.subsubdossier, self.empty_dossier, message, translated)

        self.assert_cannot_move(
            browser, self.subsubdocument, self.empty_dossier, message, translated)

    @browsing
    def test_move_dossiertemplate_to_templatefolder_is_possible(self, browser):
        self.login(self.administrator, browser)
        self.assert_can_move(browser, self.dossiertemplate, self.subtemplates)

    @browsing
    def test_moving_dossiertemplate_respects_maximum_dossier_depth_if_flag_enabled(self, browser):
        self.login(self.administrator, browser)
        api.portal.set_registry_record('respect_max_depth', True,
                                       interface=IDossierTemplateSettings)

        empty_dossiertemplate = create(Builder('dossiertemplate')
                                       .within(self.templates))

        message = u'msg_would_exceed_max_dossier_level'
        translated = u'This would exceed the maximally allowed dossier depth.'
        self.assert_cannot_move(
            browser, self.dossiertemplate, empty_dossiertemplate, message, translated)

        api.portal.set_registry_record('respect_max_depth', False,
                                       interface=IDossierTemplateSettings)

        self.assert_can_move(browser, self.dossiertemplate, empty_dossiertemplate)

    @browsing
    def test_move_tasktemplatefolder_to_templatefolder_is_possible(self, browser):
        self.login(self.administrator, browser)
        self.assert_can_move(browser, self.tasktemplatefolder, self.subtemplates)

    @browsing
    def test_can_only_move_tasktemplatefolder_into_tasktemplatefolder_if_nesting_enabled(self,
                                                                                         browser):
        self.login(self.administrator, browser)
        tasktemplatefolder = create(Builder('tasktemplatefolder').within(self.templates))

        message = u'msg_tasktemplatefolder_nesting_not_allowed'
        translated = u"It's not allowed to move tasktemplatefolders into tasktemplatefolders."
        self.assert_cannot_move(
            browser, self.tasktemplatefolder, tasktemplatefolder, message, translated)

        self.activate_feature('tasktemplatefolder_nesting')

        self.assert_can_move(browser, self.tasktemplatefolder, tasktemplatefolder)

    @browsing
    def test_move_document_when_not_all_path_elemnts_are_accessible(self, browser):
        self.login(self.administrator, browser=browser)
        subdossier = create(Builder('dossier')
                            .titled(u'Sub')
                            .within(self.protected_dossier))
        RoleAssignmentManager(subdossier).add_or_update_assignments(
            [SharingRoleAssignment(self.regular_user.id, ['Editor'])])
        doc = create(Builder('document')
                     .titled(u'doc')
                     .within(subdossier))

        self.login(self.regular_user, browser=browser)
        self.assert_can_move(browser, doc, self.dossier)
