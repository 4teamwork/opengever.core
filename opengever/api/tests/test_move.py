from Acquisition import aq_base
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser import LIB_MECHANIZE
from mock import patch
from OFS.CopySupport import CopyError
from opengever.base.model import create_session
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.bgtasks.interfaces import IBackgroundTaskSettings
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_PENDING
from opengever.bgtasks.move import MoveObjectsTask
from opengever.bgtasks.move import TASK_TYPE
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.locking.lock import MOVE_LOCK
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from plone.locking.interfaces import ILockable
import json
import transaction


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


class TestExplicitSynchronousMove(IntegrationTestCase):

    def assert_synchronous_move(self, browser, sources, destination):
        source_urls = [obj.absolute_url() for obj in sources]
        source_uids = [obj.UID() for obj in sources]
        with patch('opengever.api.move.queue_task') as queue:
            with patch('opengever.api.move.ILockable') as lockable:
                browser.open(
                    destination, view='@move',
                    data=json.dumps({'source': source_urls,
                                     'synchronous': True}),
                    method='POST', headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertFalse(queue.called)
        self.assertFalse(lockable.called)
        self.assertEqual(len(sources), len(browser.json))
        results = {item['source']: item['target'] for item in browser.json}
        self.assertItemsEqual(source_urls, results.keys())
        for source_url, uid in zip(source_urls, source_uids):
            target_url = results[source_url]
            target = destination[target_url.rsplit('/', 1)[-1]]
            self.assertEqual(target.absolute_url(), target_url)
            self.assertEqual(uid, target.UID())
            self.assertFalse(ILockable(target).locked())
        return results

    @browsing
    def test_synchronous_move_with_queue_enabled(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        self.assert_synchronous_move(browser, [self.document], self.empty_dossier)

    @browsing
    def test_synchronous_move_with_queue_disabled(self, browser):
        self.deactivate_feature('bgtasks')
        self.login(self.regular_user, browser)
        self.assert_synchronous_move(browser, [self.document], self.empty_dossier)

    @browsing
    def test_multiple_sources_from_same_parent(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        self.assert_synchronous_move(
            browser, [self.document, self.mail_eml], self.empty_dossier)

    @browsing
    def test_multiple_sources_from_different_parents(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        self.assert_synchronous_move(
            browser, [self.document, self.subdocument], self.empty_dossier)

    @browsing
    def test_collision_returns_actual_renamed_target(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        existing = create(Builder('document').within(self.empty_dossier)
                          .having(id=self.document.getId()))
        existing_uid = existing.UID()
        source_url = self.document.absolute_url()
        predicted_url = existing.absolute_url()
        results = self.assert_synchronous_move(
            browser, [self.document], self.empty_dossier)
        self.assertNotEqual(predicted_url, results[source_url])
        self.assertEqual(existing_uid, existing.UID())

    @browsing
    def test_invalid_container_propagates_paste_failure(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        source_url = self.document.absolute_url()
        uid = self.document.UID()
        with patch('opengever.api.move.queue_task') as queue:
            with patch('opengever.api.move.ILockable') as lockable:
                with browser.expect_http_error(500):
                    browser.open(
                        self.leaf_repofolder, view='@move',
                        data=json.dumps({'source': source_url,
                                         'synchronous': True}),
                        method='POST', headers=self.api_headers)
        self.assertEqual('ValueError', browser.json['type'])
        self.assertEqual('Disallowed subobject type: opengever.document.document',
                         browser.json['message'])
        self.assertEqual(source_url, self.document.absolute_url())
        self.assertEqual(uid, self.document.UID())
        self.assertFalse(ILockable(self.document).locked())
        self.assertFalse(queue.called)
        self.assertFalse(lockable.called)

    @browsing
    def test_synchronous_move_keeps_movability_checks(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        source_url = self.taskdocument.absolute_url()
        with browser.expect_http_error(403):
            browser.open(
                self.empty_dossier, view='@move',
                data=json.dumps({'source': source_url, 'synchronous': True}),
                method='POST', headers=self.api_headers)
        self.assertEqual('msg_doc_inside_task_cant_be_moved',
                         browser.json['message'])
        self.assertEqual(source_url, self.taskdocument.absolute_url())

    @browsing
    def test_non_boolean_option_is_rejected_before_mutation(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        source_url = self.document.absolute_url()
        for value in (None, 0, 1, 'true', 'false', [], {}):
            with patch('opengever.api.move.Move.clipboard') as clipboard:
                with patch('opengever.api.move.queue_task') as queue:
                    with browser.expect_http_error(400):
                        browser.open(
                            self.empty_dossier, view='@move',
                            data=json.dumps({'source': source_url,
                                             'synchronous': value}),
                            method='POST', headers=self.api_headers)
            self.assertEqual("Property 'synchronous' must be a boolean",
                             browser.json['message'])
            self.assertFalse(clipboard.called)
            self.assertFalse(queue.called)
            self.assertEqual(source_url, self.document.absolute_url())
            self.assertFalse(ILockable(self.document).locked())

    @browsing
    def test_false_option_preserves_queued_move(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        source_url = self.document.absolute_url()
        browser.open(
            self.empty_dossier, view='@move',
            data=json.dumps({'source': source_url, 'synchronous': False}),
            method='POST', headers=self.api_headers)
        self.assertEqual(202, browser.status_code)
        self.assertEqual(source_url, self.document.absolute_url())
        self.assertTrue(ILockable(self.document).locked())
        tasks = (create_session().query(BackgroundTask)
                 .filter_by(task_type=TASK_TYPE, status=TASK_STATUS_PENDING)
                 .all())
        self.assertEqual(1, len(tasks))

    @browsing
    def test_missing_sources_are_rejected_before_any_move(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        source_url = self.document.absolute_url()
        missing_url = self.dossier.absolute_url() + '/missing-document'
        for sources in ([missing_url], [source_url, missing_url]):
            with patch('opengever.api.move.Move.clipboard') as clipboard:
                with patch('opengever.api.move.queue_task') as queue:
                    with browser.expect_http_error(400):
                        browser.open(
                            self.empty_dossier, view='@move',
                            data=json.dumps({'source': sources,
                                             'synchronous': True}),
                            method='POST', headers=self.api_headers)
            self.assertEqual('Every source must resolve to an existing object',
                             browser.json['message'])
            self.assertFalse(clipboard.called)
            self.assertFalse(queue.called)
            self.assertEqual(source_url, self.document.absolute_url())
            self.assertFalse(ILockable(self.document).locked())

    @browsing
    def test_move_to_same_parent_keeps_original_location(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        source_url = self.document.absolute_url()
        results = self.assert_synchronous_move(
            browser, [self.document], self.dossier)
        self.assertEqual(source_url, results[source_url])

    @browsing
    def test_dossier_move_preserves_descendants(self, browser):
        self.activate_feature('bgtasks')
        self.login(self.regular_user, browser)
        api.portal.set_registry_record(name='maximum_dossier_depth',
                                       value=3,
                                       interface=IDossierContainerTypes)
        dossier = create(Builder('dossier').within(self.dossier))
        document = create(Builder('document').within(dossier))
        subdossier = create(Builder('dossier').within(dossier))
        subdocument = create(Builder('document').within(subdossier))
        descendants = {
            document.getId(): document.UID(),
            subdossier.getId(): subdossier.UID(),
            '{}/{}'.format(subdossier.getId(), subdocument.getId()):
                subdocument.UID(),
        }
        source_url = dossier.absolute_url()
        results = self.assert_synchronous_move(
            browser, [dossier], self.empty_dossier)
        target_url = results[source_url]
        moved = self.empty_dossier[target_url.rsplit('/', 1)[-1]]
        for path, uid in descendants.items():
            descendant = moved.restrictedTraverse(path)
            self.assertEqual(uid, descendant.UID())
            self.assertEqual('{}/{}'.format(target_url, path),
                             descendant.absolute_url())


class TestSynchronousMoveTransactions(FunctionalTestCase):

    @browsing
    def test_later_parent_paste_failure_rolls_back_entire_request(self, browser):
        # The integration traversal driver suppresses transaction aborts.
        # Use the publisher with real request transactions to verify rollback.
        browser.request_library = LIB_MECHANIZE
        browser.login()
        api.portal.set_registry_record('is_feature_enabled', True,
                                       interface=IBackgroundTaskSettings)
        sources = [create(Builder('document').within(create(Builder('dossier'))))
                   for _ in range(2)]
        destination = create(Builder('dossier'))
        source_urls = [obj.absolute_url() for obj in sources]
        source_uids = [obj.UID() for obj in sources]
        destination_url = destination.absolute_url()
        self.assertEqual([], list(destination.objectIds()))
        transaction.commit()
        destination_class = type(aq_base(destination))
        paste = destination_class.manage_pasteObjects
        pasted_results = []

        def paste_once_then_fail(context, cb_copy_data):
            if pasted_results:
                raise CopyError('Second parent paste rejected')
            result = paste(context, cb_copy_data=cb_copy_data)
            pasted_results.append(result)
            self.assertEqual(1, len(result))
            self.assertIn(result[0]['new_id'], context.objectIds())
            return result

        with patch.object(destination_class, 'manage_pasteObjects',
                          paste_once_then_fail):
            with browser.expect_http_error(500):
                browser.open(
                    destination_url, view='@move',
                    data=json.dumps({'source': source_urls,
                                     'synchronous': True}),
                    method='POST', headers=self.api_headers)
        self.assertEqual('CopyError', browser.json['type'])
        self.assertEqual('Second parent paste rejected', browser.json['message'])
        self.assertEqual(1, len(pasted_results))
        # Read through fresh requests after the failed transaction, not through
        # the source object references captured before the move.
        for source_url, uid in zip(source_urls, source_uids):
            browser.open(source_url, headers=self.api_headers)
            self.assertEqual(source_url, browser.json['@id'])
            self.assertEqual(uid, browser.json['UID'])
        browser.open(destination_url, headers=self.api_headers)
        self.assertEqual([], browser.json['items'])
