from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.move import MoveObjectsTask
from opengever.bgtasks.move import TASK_TYPE
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.locking.lock import MOVE_LOCK
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.testing import IntegrationTestCase
from plone import api
from plone.locking.interfaces import ILockable
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

    @browsing
    def test_multi_source_same_parent_queued_move_locks_and_unlocks_all_objects(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)

        document = self.document
        mail = self.mail_eml

        self.assertFalse(ILockable(document).locked())
        self.assertFalse(ILockable(mail).locked())

        browser.open(
            self.empty_dossier,
            view='@move',
            data=json.dumps({
                'source': [
                    document.absolute_url(),
                    mail.absolute_url(),
                ]}),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(202, browser.status_code)

        session = create_session()
        tasks = (session.query(BackgroundTask)
                .filter_by(task_type=TASK_TYPE, status=TASK_STATUS_PENDING)
                .all())
        self.assertEqual(1, len(tasks))
        args = json.loads(tasks[0].task_arguments)
        self.assertItemsEqual(
            [document.UID(), mail.UID()], args[u'object_uids'])

        # Both objects are locked while the task is still pending.
        self.assertTrue(ILockable(document).locked())
        self.assertTrue(ILockable(mail).locked())

        handler = MoveObjectsTask()
        handler.execute(tasks[0], lambda data: None)

        # Both objects are unlocked once the task has executed.
        self.assertFalse(ILockable(document).locked())
        self.assertFalse(ILockable(mail).locked())

    @browsing
    def test_multi_source_different_parents_queues_one_task_per_parent_with_scoped_locks(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)

        # self.document's parent is self.dossier; self.subdocument's parent
        # is self.subdossier - two distinct parents, so this must produce
        # two separate tasks, each locking only its own object.
        self.assertFalse(ILockable(self.document).locked())
        self.assertFalse(ILockable(self.subdocument).locked())

        browser.open(
            self.empty_dossier,
            view='@move',
            data=json.dumps({
                'source': [
                    self.document.absolute_url(),
                    self.subdocument.absolute_url(),
                ]}),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(202, browser.status_code)

        session = create_session()
        tasks = (session.query(BackgroundTask)
                .filter_by(task_type=TASK_TYPE, status=TASK_STATUS_PENDING)
                .all())
        self.assertEqual(2, len(tasks))

        object_uids_per_task = [
            json.loads(task.task_arguments)[u'object_uids'] for task in tasks]
        self.assertItemsEqual(
            [[self.document.UID()], [self.subdocument.UID()]],
            object_uids_per_task)

        self.assertTrue(ILockable(self.document).locked())
        self.assertTrue(ILockable(self.subdocument).locked())

    @browsing
    def test_synchronous_fallback_never_applies_move_lock(self, browser):
        self.login(self.regular_user, browser)
        api.portal.set_registry_record(
            'current_unit_id', interface=IAdminUnitConfiguration, value=u'')

        document = self.document
        self.assertFalse(ILockable(document).locked())

        browser.open(
            self.empty_dossier,
            view='@move',
            data=json.dumps({'source': document.absolute_url()}),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertFalse(ILockable(document).locked())

    def move(self, browser, destination, sources):
        browser.open(
            destination, view='@move',
            data=json.dumps({'source': sources}),
            method='POST', headers=self.api_headers)

    def assert_nothing_locked_or_queued(self, *objs):
        for obj in objs:
            self.assertFalse(ILockable(obj).locked())
        self.assertEqual(0, create_session().query(BackgroundTask).count())

    @browsing
    def test_move_with_unresolvable_sources_returns_empty_result(self, browser):
        self.login(self.regular_user, browser)
        self.move(browser, self.empty_dossier,
                  [self.dossier.absolute_url() + '/does-not-exist'])
        self.assertEqual(200, browser.status_code)
        self.assertEqual([], browser.json)

    @browsing
    def test_multi_source_collects_all_errors_in_one_forbidden(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        ILockable(self.document).lock()
        ILockable(self.mail_eml).lock()
        sources = [self.document.absolute_url(),
                   self.taskdocument.absolute_url(),
                   self.mail_eml.absolute_url(),
                   self.subdocument.absolute_url()]
        with browser.expect_http_error(code=403):
            self.move(browser, self.empty_dossier, sources)

        self.assertEqual(u'Forbidden', browser.json['type'])
        self.assertEqual(u'Inputs not valid', browser.json['translated_message'])
        fields = browser.json['additional_metadata']['fields']
        self.assertEqual(
            [self.document.absolute_url(), self.taskdocument.absolute_url(),
             self.mail_eml.absolute_url()],
            [f['field'] for f in fields])
        self.assertEqual(
            [u'ResourceLockedError', u'Forbidden', u'ResourceLockedError'],
            [f['type'] for f in fields])
        self.assertEqual(
            [self.document.title, self.taskdocument.title, self.mail_eml.title],
            [f['item_title'] for f in fields])
        self.assertEqual(
            [u'Locked documents cannot be moved.',
             u'Documents inside a task cannot be moved.',
             u'Locked documents cannot be moved.'],
            [f['translated_message'] for f in fields])
        self.assert_nothing_locked_or_queued(self.subdocument)

    @browsing
    def test_multi_source_with_flag_off_collects_all_errors(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock()
        with browser.expect_http_error(code=403):
            self.move(browser, self.empty_dossier,
                      [self.document.absolute_url(),
                       self.subdocument.absolute_url()])

        self.assertEqual(u'Inputs not valid', browser.json['translated_message'])
        fields = browser.json['additional_metadata']['fields']
        self.assertEqual([self.document.absolute_url()],
                         [f['field'] for f in fields])
        self.assertIn(self.subdocument.getId(), self.subdossier.objectIds())
        self.assertNotIn(self.subdocument.getId(), self.empty_dossier.objectIds())

    @browsing
    def test_valid_multi_source_with_flag_off_moves_all(self, browser):
        self.login(self.regular_user, browser)
        ids = [self.document.getId(), self.subdocument.getId()]
        self.move(browser, self.empty_dossier,
                  [self.document.absolute_url(), self.subdocument.absolute_url()])

        self.assertEqual(200, browser.status_code)
        for id_ in ids:
            self.assertIn(id_, self.empty_dossier.objectIds())

    @browsing
    def test_multi_source_container_and_descendant(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        api.portal.set_registry_record(name='maximum_dossier_depth', value=10,
                                       interface=IDossierContainerTypes)
        with browser.expect_http_error(code=403):
            self.move(browser, self.empty_dossier,
                      [self.dossier.absolute_url(),
                       self.subdossier.absolute_url()])

        fields = browser.json['additional_metadata']['fields']
        self.assertEqual(
            [{u'field': self.subdossier.absolute_url(),
              u'item_title': self.subdossier.title,
              u'type': u'Forbidden',
              u'translated_message': u'This item is located inside another '
                                     u'item that is being moved.'}],
            fields)
        self.assert_nothing_locked_or_queued(self.dossier, self.subdossier)

    @browsing
    def test_destination_inside_single_source_is_plain_forbidden(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403):
            self.move(browser, self.subdossier, [self.dossier.absolute_url()])

        self.assertEqual(u'Forbidden', browser.json['type'])
        self.assertEqual({}, browser.json['additional_metadata'])
        self.assertEqual(
            u'An item cannot be moved into itself or one of its subitems.',
            browser.json['translated_message'])
        self.assert_nothing_locked_or_queued(self.dossier)

    @browsing
    def test_destination_equal_to_source_is_forbidden(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403):
            self.move(browser, self.empty_dossier,
                      [self.empty_dossier.absolute_url()])

        self.assertEqual({}, browser.json['additional_metadata'])
        self.assertEqual(
            u'An item cannot be moved into itself or one of its subitems.',
            browser.json['translated_message'])
        self.assert_nothing_locked_or_queued(self.empty_dossier)

    @browsing
    def test_destination_inside_source_in_batch_gives_entry(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        api.portal.set_registry_record(name='maximum_dossier_depth', value=10,
                                       interface=IDossierContainerTypes)
        with browser.expect_http_error(code=403):
            self.move(browser, self.subdossier,
                      [self.dossier.absolute_url(), self.empty_dossier.absolute_url()])

        fields = browser.json['additional_metadata']['fields']
        self.assertEqual([self.dossier.absolute_url()],
                         [f['field'] for f in fields])
        self.assertEqual(
            u'An item cannot be moved into itself or one of its subitems.',
            fields[0]['translated_message'])
        self.assert_nothing_locked_or_queued(self.dossier, self.empty_dossier)

    @browsing
    def test_destination_with_move_lock_is_forbidden(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        ILockable(self.empty_dossier).lock(MOVE_LOCK)
        with browser.expect_http_error(code=403):
            self.move(browser, self.empty_dossier, [self.document.absolute_url()])

        self.assertEqual({}, browser.json['additional_metadata'])
        self.assertEqual(
            u'Items cannot be moved into a destination that is currently '
            u'being moved.',
            browser.json['translated_message'])
        self.assert_nothing_locked_or_queued(self.document)

    @browsing
    def test_destination_below_move_locked_ancestor_is_forbidden(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        document = create(Builder('document').within(self.empty_dossier))
        ILockable(self.dossier).lock(MOVE_LOCK)
        with browser.expect_http_error(code=403):
            self.move(browser, self.subdossier, [document.absolute_url()])

        self.assertEqual(
            u'Items cannot be moved into a destination that is currently '
            u'being moved.',
            browser.json['translated_message'])
        self.assert_nothing_locked_or_queued(document)

    @browsing
    def test_destination_lock_wins_over_source_errors_in_batch(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        ILockable(self.empty_dossier).lock(MOVE_LOCK)
        with browser.expect_http_error(code=403):
            self.move(browser, self.empty_dossier,
                      [self.taskdocument.absolute_url(),
                       self.subdocument.absolute_url()])

        self.assertEqual({}, browser.json['additional_metadata'])
        self.assertEqual(
            u'Items cannot be moved into a destination that is currently '
            u'being moved.',
            browser.json['translated_message'])
        self.assert_nothing_locked_or_queued(self.subdocument)

    @browsing
    def test_single_locked_source_returns_plain_error(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock()
        with browser.expect_http_error(code=423):
            self.move(browser, self.empty_dossier, self.document.absolute_url())

        self.assertEqual({}, browser.json['additional_metadata'])
        self.assertEqual(u'Locked documents cannot be moved.',
                         browser.json['translated_message'])

    @browsing
    def test_single_resolved_source_returns_plain_error(self, browser):
        self.login(self.regular_user, browser)
        ILockable(self.document).lock()
        for sources in ([self.document.absolute_url(), self.document.absolute_url()],
                        [self.document.absolute_url(),
                         self.dossier.absolute_url() + '/does-not-exist']):
            with browser.expect_http_error(code=423):
                self.move(browser, self.empty_dossier, sources)

            self.assertEqual({}, browser.json['additional_metadata'])
            self.assertEqual(u'Locked documents cannot be moved.',
                             browser.json['translated_message'])

    @browsing
    def test_duplicate_sources_are_moved_once(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        self.move(browser, self.empty_dossier,
                  [self.document.absolute_url(), self.document.absolute_url()])

        self.assertEqual(202, browser.status_code)
        self.assertEqual(1, len(browser.json))
        self.assertEqual(1, create_session().query(BackgroundTask).count())
