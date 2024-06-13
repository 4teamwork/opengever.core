from contextlib import contextmanager
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from mock import patch
from opengever.base.behaviors.changed import IChanged
from opengever.base.command import CreateEmailCommand
from opengever.base.oguid import Oguid
from opengever.base.touched import RECENTLY_TOUCHED_KEY
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.locking.lock import COPIED_TO_WORKSPACE_LOCK
from opengever.mail.tests import MAIL_DATA
from opengever.testing.assets import load
from opengever.workspaceclient.exceptions import CopyFromWorkspaceForbidden
from opengever.workspaceclient.exceptions import CopyToWorkspaceForbidden
from opengever.workspaceclient.exceptions import WorkspaceNotLinked
from opengever.workspaceclient.interfaces import ILinkedDocuments
from opengever.workspaceclient.interfaces import ILinkedToWorkspace
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from plone.locking.interfaces import ILockable
from plone.uuid.interfaces import IUUID
from tzlocal import get_localzone
from zExceptions import BadRequest
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
import pytz
import transaction


@contextmanager
def auto_commit_after_request(client):
    """This contextmanager injects a session hook for the current client
    session to commit the transaction after each request.

    This is required in some functional non-browser tests where we perform
    multiple subrequests in one function call.

    This is not required for browser-tests or production environments because
    the transaction will be committed automatically as soon as a request is
    finished.
    """
    def commit_transaction_hook(*args, **kwargs):
        transaction.commit()

    client_session_hooks = client.session.session.hooks
    original_hooks = list(client_session_hooks['response'])
    client_session_hooks['response'].append(commit_transaction_hook)

    try:
        yield
    finally:
        client_session_hooks['response'] = original_hooks


class TestLinkedWorkspaces(FunctionalWorkspaceClientTestCase):

    def test_list_linked_workspaces(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)

            self.assertEqual([], manager.list().get('items'))

            manager.storage.add(self.workspace.UID())

            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in manager.list().get('items')])

    def test_batching_in_list_linked_workspaces(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            workspace2 = create(Builder('workspace').within(self.workspace_root))
            self.grant('WorkspaceMember', on=workspace2)
            manager.storage.add(workspace2.UID())

            self.assertEqual(
                [self.workspace.absolute_url(), workspace2.absolute_url()],
                [workspace.get('@id') for workspace in manager.list().get('items')])

            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in manager.list(b_size=1).get('items')])

            self.assertEqual(
                [workspace2.absolute_url()],
                [workspace.get('@id') for workspace in
                 manager.list(b_size=1, b_start=1).get('items')])

    def test_list_skips_workspaces_if_no_view_permission(self):
        unauthorized_workspace = create(Builder('workspace').within(
            self.workspace_root))
        self.grant('', on=unauthorized_workspace)

        authorized_workspace = create(Builder('workspace').within(
            self.workspace_root))
        self.grant('View', on=unauthorized_workspace)

        self.assertTrue(api.user.has_permission('View', obj=self.workspace))
        self.assertTrue(api.user.has_permission(
            'View', obj=authorized_workspace))
        self.assertFalse(api.user.has_permission(
            'View', obj=unauthorized_workspace))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            manager.storage.add(authorized_workspace.UID())
            manager.storage.add(unauthorized_workspace.UID())

            self.assertItemsEqual(
                [self.workspace.absolute_url(), authorized_workspace.absolute_url()],
                [workspace.get('@id') for workspace in manager.list().get('items')])

            self.grant('WorkspaceMember', on=unauthorized_workspace)
            transaction.commit()

            self.invalidate_cache()
            self.assertItemsEqual(
                [self.workspace.absolute_url(),
                 authorized_workspace.absolute_url(),
                 unauthorized_workspace.absolute_url()],
                [workspace.get('@id') for workspace in manager.list().get('items')])

    def test_cache_list_stored_workspaces(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            self.workspace.title = 'Old title'
            self.workspace.reindexObject()
            transaction.commit()

            self.assertEqual(
                ['Old title'],
                [workspace.get('title') for workspace in manager.list().get('items')])

            self.workspace.title = 'New title'
            self.workspace.reindexObject()
            transaction.commit()

            self.assertEqual(
                ['Old title'],
                [workspace.get('title') for workspace in manager.list().get('items')])

            self.invalidate_cache()
            self.assertEqual(
                ['New title'],
                [workspace.get('title') for workspace in manager.list().get('items')])

    def test_create_workspace_will_store_workspace_in_the_storage(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            self.assertEqual([], manager.list().get('items'))

            # This prevents a database conflict error,
            # otherwise both the dossier and the workspace will be modified.
            # This is a testing issue (doesn't happen in production)
            alsoProvides(self.dossier, ILinkedToWorkspace)

            with self.observe_children(self.workspace_root) as children:
                response = manager.create(title=u"My new w\xf6rkspace")
                transaction.commit()

            self.assertEqual(u"My new w\xf6rkspace", response.get('title'))

            workspace = children['added'].pop()
            self.assertEqual([workspace.absolute_url()],
                             [ws.get('@id') for ws in manager.list().get('items')])
            self.assertEqual(workspace.external_reference, Oguid.for_object(self.dossier).id)

    def test_link_to_workspace(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            self.assertEqual([], manager.list().get('items'))

            # This prevents a database conflict error,
            # otherwise both the dossier and the workspace will be modified.
            # This is a testing issue (doesn't happen in production)
            alsoProvides(self.dossier, ILinkedToWorkspace)

            manager.link_to_workspace(self.workspace.UID())
            transaction.commit()
            self.assertEqual([self.workspace.absolute_url()],
                             [ws.get('@id') for ws in manager.list().get('items')])
            self.assertEqual(self.workspace.external_reference, Oguid.for_object(self.dossier).id)

    def test_copy_document_without_file_to_workspace(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .having(preserved_as_paper=True))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.workspace) as children:
                response = manager.copy_document_to_workspace(
                    document, self.workspace.UID())
                transaction.commit()

            self.assertEqual(1, len(children['added']))
            workspace_document = children['added'].pop()

            self.assertEqual(workspace_document.absolute_url(), response.get('@id'))
            self.assertEqual(workspace_document.title, document.title)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(document),
                manager._serialized_document_schema_fields(workspace_document))

    def test_copy_document_to_workspace_raises_error_if_workspace_is_not_linked_to_the_dossier(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .having(preserved_as_paper=True))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)

            self.assertNotIn(self.workspace.UID(), manager.storage)
            with self.assertRaises(WorkspaceNotLinked):
                manager.copy_document_to_workspace(document, self.workspace.UID())

    def test_copy_document_to_workspace_raises_error_if_workspace_could_not_be_found(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .having(preserved_as_paper=True))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add('removed-workspace-uid')

            with self.assertRaises(LookupError):
                manager.copy_document_to_workspace(document, 'removed-workspace-uid')

    def test_copy_document_with_file_to_a_workspace(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .with_dummy_content())

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.workspace) as children:
                with auto_commit_after_request(manager.client):
                    response = manager.copy_document_to_workspace(
                        document, self.workspace.UID())

            self.assertEqual(1, len(children['added']))
            workspace_document = children['added'].pop()

            self.assertEqual(workspace_document.absolute_url(),
                             response.get('@id'))
            self.assertEqual(workspace_document.title, document.title)
            self.assertEqual(workspace_document.file.open().read(),
                             document.file.open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(document),
                manager._serialized_document_schema_fields(workspace_document))

    def test_copy_eml_mail_to_a_workspace(self):
        mail = create(Builder("mail")
                      .with_message(MAIL_DATA)
                      .within(self.dossier))
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            with self.observe_children(self.workspace) as children:
                with auto_commit_after_request(manager.client):
                    response = manager.copy_document_to_workspace(
                        mail, self.workspace.UID())

            self.assertEqual(1, len(children['added']))
            workspace_mail = children['added'].pop()

            self.assertEqual(workspace_mail.absolute_url(), response.get('@id'))
            self.assertEqual(workspace_mail.title, mail.title)

            self.assertEqual(workspace_mail.get_file().open().read(),
                             mail.get_file().open().read())

            self.assertEqual('message/rfc822', workspace_mail.message.contentType)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))

    def test_copy_document_to_a_workspace_drops_related_items(self):
        related_document = create(Builder('document')
                                  .within(self.dossier)
                                  .with_dummy_content())
        document = create(Builder('document')
                          .within(self.dossier)
                          .with_dummy_content()
                          .having(relatedItems=[related_document]))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.workspace) as children:
                with auto_commit_after_request(manager.client):
                    response = manager.copy_document_to_workspace(
                        document, self.workspace.UID())

            self.assertEqual(1, len(children['added']))
            workspace_document = children['added'].pop()

            self.assertEqual(workspace_document.absolute_url(),
                             response.get('@id'))
            self.assertEqual(workspace_document.title, document.title)
            self.assertEqual(
                [], IRelatedDocuments(workspace_document).relatedItems)

    def test_copy_msg_mail_to_a_workspace(self):

        msg = load('testmail.msg')
        command = CreateEmailCommand(
            self.dossier, 'testm\xc3\xa4il.msg', msg)
        mail = command.execute()
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.workspace) as children:
                with auto_commit_after_request(manager.client):
                    response = manager.copy_document_to_workspace(
                        mail, self.workspace.UID())

            self.assertEqual(1, len(children['added']))
            workspace_mail = children['added'].pop()

            self.assertEqual(workspace_mail.absolute_url(), response.get('@id'))
            self.assertEqual(workspace_mail.title, mail.title)

            self.assertEqual(workspace_mail.get_file().open().read(),
                             mail.get_file().open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))

    def test_copy_checked_out_doc_to_workspace_is_prevented(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .with_dummy_content())

        manager = getMultiAdapter((document, self.request), ICheckinCheckoutManager)
        manager.checkout()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.workspace) as children:
                with auto_commit_after_request(manager.client):
                    with self.assertRaises(CopyToWorkspaceForbidden):
                        manager.copy_document_to_workspace(
                            document, self.workspace.UID())

            self.assertEqual(0, len(children['added']))

    def test_locking_document_when_copying_it_to_a_workspace(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .with_dummy_content())

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.workspace) as children:
                with auto_commit_after_request(manager.client):
                    manager.copy_document_to_workspace(
                        document, self.workspace.UID())

            self.assertEqual(1, len(children['added']))
            self.assertFalse(ILockable(document).locked())

            with self.observe_children(self.workspace) as children:
                with auto_commit_after_request(manager.client):
                    manager.copy_document_to_workspace(
                        document, self.workspace.UID(), lock=True)

            self.assertEqual(1, len(children['added']))
            self.assertTrue(ILockable(document).locked())

            lock_infos = ILockable(document).lock_info()
            self.assertEqual(1, len(lock_infos))
            self.assertEqual(u'document.copied_to_workspace.lock',
                             lock_infos[0]['type'].__name__)

    def test_locking_mail_is_ignored_when_copying_it_to_a_workspace(self):
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_dummy_message())

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.workspace) as children:
                with auto_commit_after_request(manager.client):
                    manager.copy_document_to_workspace(
                        mail, self.workspace.UID(), lock=True)

            self.assertEqual(1, len(children['added']))
            self.assertFalse(ILockable(mail).locked())

    def test_has_linked_workspaces(self):
        manager = ILinkedWorkspaces(self.dossier)

        self.assertFalse(manager.has_linked_workspaces())

        manager.storage.add(self.workspace.UID())

        self.assertTrue(manager.has_linked_workspaces())

    def test_list_documents_in_linked_workspace_raises_if_workspace_is_not_linked(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            self.assertNotIn(self.workspace.UID(), manager.storage)
            with self.assertRaises(WorkspaceNotLinked):
                manager.list_documents_in_linked_workspace(self.workspace.UID())

    def test_list_documents_in_linked_workspace_raises_if_workspace_could_not_be_found(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add('removed-workspace-uid')

            with self.assertRaises(LookupError):
                manager.list_documents_in_linked_workspace('removed-workspace-uid')

    def test_list_documents_in_linked_workspace(self):
        document = create(Builder('document')
                          .within(self.workspace))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            documents = manager.list_documents_in_linked_workspace(
                self.workspace.UID())
            expected_url = (
                '{}/@search?portal_type=opengever.document.document&'
                'portal_type=ftw.mail.mail&metadata_fields=UID&'
                'metadata_fields=filename&metadata_fields=checked_out'.format(
                    self.workspace.absolute_url()))
            self.assertEqual(expected_url, documents['@id'])
            self.assertEqual(1, documents['items_total'])
            self.assertEqual(
                {u'@id': document.absolute_url(),
                 u'@type': u'opengever.document.document',
                 u'UID': document.UID(),
                 u'checked_out': u'',
                 u'description': u'',
                 u'file_extension': u'',
                 u'filename': u'',
                 u'is_leafnode': None,
                 u'review_state': u'opengever_workspace_document--STATUS--active',
                 u'title': u'Testdokum\xe4nt'},
                documents['items'][0])

    def test_list_documents_in_linked_workspace_handles_batching(self):
        document1 = create(Builder('document')
                           .within(self.workspace))
        document2 = create(Builder('document')
                           .within(self.workspace))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            self.assertEqual(
                [document1.absolute_url(), document2.absolute_url()],
                [doc.get('@id') for doc in manager.list_documents_in_linked_workspace(
                    self.workspace.UID()).get('items')])

            self.assertEqual(
                [document1.absolute_url()],
                [doc.get('@id') for doc in manager.list_documents_in_linked_workspace(
                    self.workspace.UID(), b_size=1).get('items')])

            self.assertEqual(
                [document2.absolute_url()],
                [doc.get('@id') for doc in manager.list_documents_in_linked_workspace(
                    self.workspace.UID(), b_size=1, b_start=1).get('items')])

    def test_copy_document_with_file_from_a_workspace(self):
        document = create(Builder('document')
                          .within(self.workspace)
                          .with_dummy_content())
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                        self.workspace.UID(), document.UID())

            self.assertEqual(1, len(children['added']))
            workspace_document = children['added'].pop()
            self.assertEqual(workspace_document, dst_doc)

            self.assertEqual(document.title, workspace_document.title)
            self.assertEqual(document.description, workspace_document.description)
            self.assertEqual(document.file.open().read(),
                             workspace_document.file.open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(document),
                manager._serialized_document_schema_fields(workspace_document))

            document_journal = self.get_journal_entries(workspace_document)
            self.assertEqual(2, len(document_journal))

            self.assert_journal_entry(
                workspace_document,
                action_type='Document created via copy from teamraum',
                title=u'Initial version - Document copied from teamraum %s.' % self.workspace.title,
            )

    def test_copy_document_from_workspace_as_new_version(self):
        gever_doc = create(Builder('document')
                           .within(self.dossier)
                           .with_dummy_content())

        self.assertIsNone(Versioner(gever_doc).get_current_version_id())
        self.assertFalse(Versioner(gever_doc).has_initial_version())

        initial_content = gever_doc.file.data
        initial_filename = gever_doc.file.filename
        initial_content_type = gever_doc.file.contentType

        self.assertEqual('Test data', initial_content)
        self.assertEqual(u'Testdokumaent.doc', initial_filename)
        self.assertEqual(u'application/msword', initial_content_type)

        new_content = 'Content produced in Workspace'
        new_filename = u'workspace.pdf'

        workspace_doc = create(Builder('document')
                               .within(self.workspace)
                               .attach_file_containing(new_content,
                                                       name=new_filename))

        ILinkedDocuments(workspace_doc).link_gever_document(IUUID(gever_doc))
        ILinkedDocuments(gever_doc).link_workspace_document(IUUID(workspace_doc))

        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            freeze_time = datetime(2018, 4, 30, 7, 30, tzinfo=pytz.UTC)
            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    with freeze(freeze_time):
                        dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                            self.workspace.UID(), workspace_doc.UID(),
                            as_new_version=True)

            self.assertEqual(0, len(children['added']))
            self.assertEqual(gever_doc, dst_doc)

            self.assertTrue(Versioner(gever_doc).has_initial_version())
            self.assertEqual(1, Versioner(gever_doc).get_current_version_id())

            self.assertEqual(new_content, gever_doc.file.data)
            self.assertEqual(u'Testdokumaent.pdf', gever_doc.file.filename)
            self.assertEqual(u'application/pdf', gever_doc.file.contentType)

            initial_version = Versioner(gever_doc).retrieve(0)
            initial_version_md = Versioner(gever_doc).retrieve_version(0)
            new_version = Versioner(gever_doc).retrieve(1)
            new_version_md = Versioner(gever_doc).retrieve_version(1)

            self.assertEqual(initial_content, initial_version.file.data)
            self.assertEqual(initial_filename, initial_version.file.filename)
            self.assertEqual(u'Initial version', initial_version_md.comment)

            self.assertEqual(new_content, new_version.file.data)
            self.assertEqual(u'Testdokumaent.pdf', new_version.file.filename)
            self.assertEqual(u'application/pdf', new_version.file.contentType)
            self.assertEqual(u'Document copied back from teamraum', new_version_md.comment)

            document_journal = self.get_journal_entries(gever_doc)
            self.assertEqual(2, len(document_journal))

            self.assert_journal_entry(
                gever_doc,
                action_type='Document retrieved as new version from teamraum',
                title=u'Document unlocked - created new version with document from teamraum.',
            )

            self.assert_journal_entry(
                self.dossier,
                action_type='Document retrieved from teamraum',
                title=u'Document Testdokum\xe4nt copied back from workspace.',
            )
            self.assertEqual(freeze_time, IChanged(gever_doc).changed)
            local_freeze_time = freeze_time.astimezone(get_localzone())
            last_entry = IAnnotations(self.portal)[RECENTLY_TOUCHED_KEY]['test_user_1_'][-1]
            self.assertEqual(
                {'last_touched': local_freeze_time, 'uid': IUUID(gever_doc)},
                last_entry)

    def test_copy_document_from_a_workspace_and_trash_tr_document(self):
        document = create(Builder('document')
                          .within(self.workspace)
                          .with_dummy_content())
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    # Patch client request to @trash to avoid ConflictErrors
                    with patch('opengever.workspaceclient.client'
                               '.WorkspaceClient.trash_document') as trash_document:
                        dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                            self.workspace.UID(), document.UID(),
                            trash_tr_document=True)

            # WorkspaceClient should have been instructed to trash the TR doc
            trash_document.assert_called_with(document.absolute_url())

            self.assertEqual(1, len(children['added']))
            gever_document = children['added'].pop()
            self.assertEqual(gever_document, dst_doc)

    def test_copy_document_from_a_workspace_as_version_and_trash_tr_document(self):
        gever_doc = create(Builder('document')
                           .within(self.dossier)
                           .with_dummy_content())

        self.assertIsNone(Versioner(gever_doc).get_current_version_id())
        self.assertFalse(Versioner(gever_doc).has_initial_version())

        new_content = 'Content produced in Workspace'
        new_filename = u'workspace.doc'

        workspace_doc = create(Builder('document')
                               .within(self.workspace)
                               .attach_file_containing(new_content,
                                                       name=new_filename))

        ILinkedDocuments(workspace_doc).link_gever_document(IUUID(gever_doc))
        ILinkedDocuments(gever_doc).link_workspace_document(IUUID(workspace_doc))

        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    # Patch client request to @trash to avoid ConflictErrors
                    with patch('opengever.workspaceclient.client'
                               '.WorkspaceClient.trash_document') as trash_document:
                        dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                            self.workspace.UID(), workspace_doc.UID(),
                            as_new_version=True, trash_tr_document=True)

            # WorkspaceClient should have been instructed to trash the TR doc
            trash_document.assert_called_with(workspace_doc.absolute_url())

            self.assertEqual(0, len(children['added']))
            self.assertEqual(gever_doc, dst_doc)

            self.assertTrue(Versioner(gever_doc).has_initial_version())
            self.assertEqual(1, Versioner(gever_doc).get_current_version_id())

    def test_copy_document_from_workspace_as_new_version_unlocks_document(self):
        gever_doc = create(Builder('document')
                           .within(self.dossier)
                           .with_dummy_content())

        ILockable(gever_doc).lock(COPIED_TO_WORKSPACE_LOCK)

        workspace_doc = create(Builder('document')
                               .within(self.workspace)
                               .attach_file_containing('foo', name=u'foo.doc'))

        ILinkedDocuments(workspace_doc).link_gever_document(IUUID(gever_doc))
        ILinkedDocuments(gever_doc).link_workspace_document(IUUID(workspace_doc))

        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with auto_commit_after_request(manager.client):
                dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                    self.workspace.UID(), workspace_doc.UID(),
                    as_new_version=True)

            self.assertEqual(gever_doc, dst_doc)
            self.assertFalse(ILockable(gever_doc).locked())

    def test_copy_document_from_workspace_as_new_version_for_invalid_uid(self):
        workspace_doc = create(Builder('document')
                               .within(self.workspace)
                               .attach_file_containing('foo', name=u'foo.doc'))

        ILinkedDocuments(workspace_doc).link_gever_document("invalid")
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            with self.observe_children(self.dossier) as children,\
                 auto_commit_after_request(manager.client):
                dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                    self.workspace.UID(), workspace_doc.UID(),
                    as_new_version=True)

        self.assertEqual(1, len(children['added']))
        self.assertEqual(children['added'].pop(), dst_doc)
        self.assertEqual(workspace_doc.file.data, dst_doc.file.data)

    def test_copy_unlinked_document_from_workspace_as_new_version(self):
        """Retrieving an unlinked document from a workspace to GEVER should
        always create a copy, even when `as_new_version=True` was given.
        """
        workspace_doc = create(Builder('document')
                               .within(self.workspace)
                               .with_dummy_content())
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                        self.workspace.UID(), workspace_doc.UID(),
                        as_new_version=True)

            self.assertEqual(1, len(children['added']))
            new_gever_doc = children['added'].pop()
            self.assertEqual(new_gever_doc, dst_doc)
            self.assertEqual(workspace_doc.title, new_gever_doc.title)

    def test_copy_document_without_file_from_a_workspace(self):
        document = create(Builder('document')
                          .within(self.workspace))
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                        self.workspace.UID(), document.UID())

            self.assertEqual(1, len(children['added']))
            workspace_document = children['added'].pop()
            self.assertEqual(workspace_document, dst_doc)

            self.assertEqual(document.title, workspace_document.title)
            self.assertEqual(document.description, workspace_document.description)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(document),
                manager._serialized_document_schema_fields(workspace_document))

    def test_copy_doc_without_file_from_workspace_as_new_version(self):
        """A document without file should always be retrieved as a copy, even
        when linked and `as_new_version=True` was specified.
        """
        workspace_doc = create(Builder('document')
                               .within(self.workspace))

        gever_doc = create(Builder('document')
                           .within(self.dossier))

        # Documents without a file are never linked by the current
        # implementation. But even if they were, no attempt at creating a
        # version should be made.
        ILinkedDocuments(workspace_doc).link_gever_document(IUUID(gever_doc))
        ILinkedDocuments(gever_doc).link_workspace_document(IUUID(workspace_doc))
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                        self.workspace.UID(), workspace_doc.UID(), as_new_version=True)

            self.assertEqual(1, len(children['added']))
            new_doc = children['added'].pop()
            self.assertEqual(new_doc, dst_doc)

    def test_copy_eml_mail_from_a_workspace(self):
        mail = create(Builder("mail")
                      .with_message(MAIL_DATA)
                      .within(self.workspace))
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                        self.workspace.UID(), mail.UID())

            self.assertEqual(1, len(children['added']))
            workspace_mail = children['added'].pop()
            self.assertEqual(workspace_mail, dst_doc)

            self.assertEqual(mail.title, workspace_mail.title)
            self.assertEqual(mail.description, workspace_mail.description)
            self.assertEqual(workspace_mail.get_file().open().read(),
                             mail.get_file().open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))

    def test_copy_eml_mail_from_workspace_as_new_version(self):
        """A mail should always be retrieved as a copy, even when linked and
        `as_new_version=True` was specified.
        """
        workspace_mail = create(Builder("mail")
                                .with_message(MAIL_DATA)
                                .within(self.workspace))

        gever_doc = create(Builder('document')
                           .within(self.dossier))

        # Mails are never linked by the current implementation. But even if
        # they were, no attempt at creating a version should be made.
        ILinkedDocuments(workspace_mail).link_gever_document(IUUID(gever_doc))
        ILinkedDocuments(gever_doc).link_workspace_document(IUUID(workspace_mail))
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                        self.workspace.UID(), workspace_mail.UID(), as_new_version=True)

            self.assertEqual(1, len(children['added']))
            new_mail = children['added'].pop()
            self.assertEqual(new_mail, dst_doc)

    def test_copy_msg_mail_from_a_workspace(self):
        msg = load('testmail.msg')
        command = CreateEmailCommand(self.workspace, 'testm\xc3\xa4il.msg', msg)
        mail = command.execute()
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                        self.workspace.UID(), mail.UID())

            self.assertEqual(1, len(children['added']))
            workspace_mail = children['added'].pop()
            self.assertEqual(workspace_mail, dst_doc)

            self.assertEqual(mail.title, workspace_mail.title)
            self.assertEqual(mail.description, workspace_mail.description)
            self.assertEqual(workspace_mail.get_file().open().read(),
                             mail.get_file().open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))

    def test_copying_document_from_workspace_is_prevented_if_checked_out(self):
        document = create(Builder('document')
                          .within(self.workspace)
                          .with_dummy_content())

        manager = getMultiAdapter((document, self.request), ICheckinCheckoutManager)
        manager.checkout()

        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    with self.assertRaises(CopyFromWorkspaceForbidden):
                        dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                            self.workspace.UID(), document.UID())

            self.assertEqual(0, len(children['added']))


class TestMoveLinkedWorkspacesDossiers(FunctionalWorkspaceClientTestCase):

    def test_move_dossier_inside_a_dossier_moves_linked_workspace_information_to_main_dossier(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            alsoProvides(self.dossier, ILinkedToWorkspace)
            self.dossier.reindexObject(idxs=['object_provides'])
            self.workspace.external_reference = 'an oguid'
            self.workspace.gever_url = u'url'

            target_dossier = create(Builder('dossier'))
            with auto_commit_after_request(manager.client):
                api.content.move(source=self.dossier, target=target_dossier)

            self.assertTrue(ILinkedToWorkspace.providedBy(target_dossier))
            self.assertFalse(ILinkedToWorkspace.providedBy(self.dossier))

            self.assertEqual({'items_total': 0, 'items': []},
                             ILinkedWorkspaces(self.dossier).list())

            target_dossier_adapter = ILinkedWorkspaces(target_dossier)
            self.assertEqual(1, target_dossier_adapter.list()['items_total'])
            self.assertIn(self.workspace.UID(), target_dossier_adapter.storage)
            gever_url = '{}/@resolve-oguid?oguid={}'.format(
                api.portal.get().absolute_url(), Oguid.for_object(target_dossier).id)
            self.assertEqual(Oguid.for_object(target_dossier).id, self.workspace.external_reference)
            self.assertEqual(gever_url, self.workspace.gever_url)


class TestLinkedWorkspacesJournalization(FunctionalWorkspaceClientTestCase):

    def test_copying_document_to_a_workspace_is_journalized(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .with_dummy_content())

        self.assertEqual(2, len(self.get_journal_entries(self.dossier)))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            with auto_commit_after_request(manager.client):
                manager.copy_document_to_workspace(document, self.workspace.UID())

        self.assertEqual(3, len(self.get_journal_entries(self.dossier)))

        self.assertEqual(
            [{'id': Oguid.for_object(document).id, 'title': document.title}],
            self.get_journal_entry(self.dossier, -1)['action']['documents'])

        self.assert_journal_entry(
            self.dossier,
            'Document copied to workspace',
            u'Document Testdokum\xe4nt copied to workspace Ein Teamraum.')

    def test_workspace_creation_is_journalized(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            self.assertEqual(1, len(self.get_journal_entries(self.dossier)))

            # This prevents a database conflict error,
            # otherwise both the dossier and the workspace will be modified.
            # This is a testing issue (doesn't happen in production)
            alsoProvides(self.dossier, ILinkedToWorkspace)

            manager.create(title=u"My new w\xf6rkspace")
            transaction.commit()

        self.assertEqual(2, len(self.get_journal_entries(self.dossier)))

        self.assert_journal_entry(
            self.dossier,
            'Linked workspace created',
            u'Linked workspace My new w\xf6rkspace created.')

    def test_workspace_linking_is_journalized(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            self.assertEqual(1, len(self.get_journal_entries(self.dossier)))

            # This prevents a database conflict error,
            # otherwise both the dossier and the workspace will be modified.
            # This is a testing issue (doesn't happen in production)
            alsoProvides(self.dossier, ILinkedToWorkspace)

            manager.link_to_workspace(self.workspace.UID())
            transaction.commit()

        journal_entries = self.get_journal_entries(self.dossier)
        self.assertEqual(2, len(journal_entries))

        self.assert_journal_entry(self.dossier, 'Linked to workspace',
                                  u'Linked to workspace {}.'.format(self.workspace.title))

    def test_copying_document_from_workspace_is_journalized(self):
        document = create(Builder('document')
                          .within(self.workspace)
                          .with_dummy_content())
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            self.assertEqual(1, len(self.get_journal_entries(self.dossier)))

            with auto_commit_after_request(manager.client):
                dst_doc, retrieval_mode = manager.copy_document_from_workspace(
                    self.workspace.UID(), document.UID())

        self.assertEqual(3, len(self.get_journal_entries(self.dossier)))

        self.assert_journal_entry(
            self.dossier,
            'Document copied from workspace',
            u'Document Testdokum\xe4nt copied from workspace Ein Teamraum as a new document.',
            entry=-1)

        self.assert_journal_entry(
            self.dossier,
            'Document added',
            u'Document added: Testdokum\xe4nt',
            entry=-2)


class TestUnlinkWorkspace(FunctionalWorkspaceClientTestCase):

    def test_unlink_removes_workspace_uid_from_storage(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with auto_commit_after_request(manager.client):
                manager.unlink_workspace(self.workspace.UID())

            self.assertEqual([], manager.storage.list())

    def test_removes_marker_interface_if_no_linked_workspaces_exists(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            workspace_2 = create(Builder('workspace')
                                 .titled(u'A Workspace')
                                 .within(self.workspace_root))

            with patch('opengever.workspaceclient.client.WorkspaceClient.link_to_workspace') as link_to_workspace:
                link_to_workspace.return_value = {'UID': self.workspace.UID()}
                manager.link_to_workspace(self.workspace.UID())

            with patch('opengever.workspaceclient.client.WorkspaceClient.link_to_workspace') as link_to_workspace:
                link_to_workspace.return_value = {'UID': workspace_2.UID()}
                manager.link_to_workspace(workspace_2.UID())

            manager.unlink_workspace(self.workspace.UID())
            self.assertTrue(ILinkedToWorkspace.providedBy(self.dossier))

            manager.unlink_workspace(workspace_2.UID())
            self.assertFalse(ILinkedToWorkspace.providedBy(self.dossier))

    def test_unlink_workspace_from_closed_dossier(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.expired_dossier)
            manager.storage.add(self.workspace.UID())

            with auto_commit_after_request(manager.client):
                manager.unlink_workspace(self.workspace.UID())

            self.assertEqual([], manager.storage.list())

    def test_unlink_is_journalized(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with auto_commit_after_request(manager.client):
                manager.unlink_workspace(self.workspace.UID())

            self.assert_journal_entry(self.dossier, 'Unlinked workspace',
                                      u'Unlinked workspace Ein Teamraum.')

    def test_unlink_workspace_unlocks_linked_documents(self):
        with self.workspace_client_env():
            workspace_2 = create(Builder('workspace')
                              .within(self.workspace_root))

            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            manager.storage.add(workspace_2.UID())

            document = create(Builder('document')
                              .within(self.dossier)
                              .attach_file_containing('DATA', u'test.txt'))
            document_2 = create(Builder('document')
                                .within(self.dossier)
                                .attach_file_containing('DATA', u'test.txt'))

            manager.copy_document_to_workspace(
                document, self.workspace.UID(), lock=True)
            manager.copy_document_to_workspace(
                document_2, workspace_2.UID(), lock=True)

            self.assertTrue(ILockable(document).locked())
            self.assertTrue(ILockable(document_2).locked())

            manager.unlink_workspace(self.workspace.UID())

            self.assertTrue(ILockable(document_2).locked())
            self.assertFalse(ILockable(document).locked())

    def test_raises_bad_request_if_not_all_linked_documents_are_accessible(self):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            subdossier = create(Builder('dossier')
                              .within(self.dossier))
            document = create(Builder('document')
                              .within(subdossier)
                              .attach_file_containing('DATA', u'test.txt'))

            ILinkedDocuments(document).link_workspace_document('WORKSPACE_DOC_UID')
            ILockable(document).lock(COPIED_TO_WORKSPACE_LOCK)

            # make document no longer accessible
            document.manage_permission("View", roles=[])
            document.reindexObject()
            transaction.commit()

            # Patch client request to avoid ConflictErrors
            with patch('opengever.api.linked_workspaces.'
                       'ListLinkedDocumentUIDsFromWorkspace.reply') as linked_docs_reply:

                linked_docs_reply.return_value = {
                    'gever_doc_uids': [document.UID()]}

                with self.assertRaises(BadRequest) as cm:
                    manager.unlink_workspace(self.workspace.UID())

                self.assertEqual(
                    'You are not allowed to access and unlock all linked '
                    'documents, unlinking this workspace is not possible.',
                    str(cm.exception))
