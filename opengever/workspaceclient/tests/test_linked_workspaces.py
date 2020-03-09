from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.command import CreateEmailCommand
from opengever.mail.tests import MAIL_DATA
from opengever.testing.assets import load
from opengever.workspaceclient.exceptions import WorkspaceNotLinked
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from zope.component import getAdapter
from zope.component.interfaces import ComponentLookupError
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
                [workspace.get('@id') for workspace in manager.list(b_size=1, b_start=1).get('items')])

    def test_list_skips_workspaces_if_no_view_permission(self):
        unauthorized_workspace = create(Builder('workspace').within(self.workspace_root))
        self.grant('', on=unauthorized_workspace)

        authorized_workspace = create(Builder('workspace').within(self.workspace_root))
        self.grant('View', on=unauthorized_workspace)

        self.assertTrue(api.user.has_permission('View', obj=self.workspace))
        self.assertTrue(api.user.has_permission('View', obj=authorized_workspace))
        self.assertFalse(api.user.has_permission('View', obj=unauthorized_workspace))

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

            self.assertEqual(['Old title'],
                             [workspace.get('title') for workspace in manager.list().get('items')])

            self.workspace.title = 'New title'
            self.workspace.reindexObject()
            transaction.commit()

            self.assertEqual(['Old title'],
                             [workspace.get('title') for workspace in manager.list().get('items')])

            self.invalidate_cache()
            self.assertEqual(['New title'],
                             [workspace.get('title') for workspace in manager.list().get('items')])

    def test_create_workspace_will_store_workspace_in_the_storage(self):
        with self.workspace_client_env() as client:
            manager = ILinkedWorkspaces(self.dossier)
            self.assertEqual([], manager.list().get('items'))

            with self.observe_children(self.workspace_root) as children:
                response = manager.create(title=u"My new w\xf6rkspace")
                transaction.commit()

            self.assertEqual(u"My new w\xf6rkspace", response.get('title'))

            workspace = children['added'].pop()
            self.assertEqual([workspace.absolute_url()],
                             [ws.get('@id') for ws in manager.list().get('items')])

    def test_subdossiers_do_not_provided_linked_workspaces(self):
        subdossier = create(Builder('dossier').within(self.dossier))

        with self.workspace_client_env():
            self.assertTrue(getAdapter(self.dossier, ILinkedWorkspaces))

            with self.assertRaises(ComponentLookupError):
                getAdapter(subdossier, ILinkedWorkspaces)

    def test_copy_document_without_file_to_workspace(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .having(preserved_as_paper=True))

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.workspace) as children:
                response = manager.copy_document_to_workspace(document, self.workspace.UID())
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
                    response = manager.copy_document_to_workspace(document, self.workspace.UID())

            self.assertEqual(1, len(children['added']))
            workspace_document = children['added'].pop()

            self.assertEqual(workspace_document.absolute_url(), response.get('@id'))
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
                    response = manager.copy_document_to_workspace(mail, self.workspace.UID())

            self.assertEqual(1, len(children['added']))
            workspace_mail = children['added'].pop()

            self.assertEqual(workspace_mail.absolute_url(), response.get('@id'))
            self.assertEqual(workspace_mail.title, mail.title)

            self.assertEqual(workspace_mail.get_file().open().read(),
                             mail.get_file().open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))

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
                    response = manager.copy_document_to_workspace(mail, self.workspace.UID())

            self.assertEqual(1, len(children['added']))
            workspace_mail = children['added'].pop()

            self.assertEqual(workspace_mail.absolute_url(), response.get('@id'))
            self.assertEqual(workspace_mail.title, mail.title)

            self.assertEqual(workspace_mail.get_file().open().read(),
                             mail.get_file().open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))

    def test_has_linked_workspaces(self):
        with self.workspace_client_env():
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

            documents = manager.list_documents_in_linked_workspace(self.workspace.UID())
            expected_url = (
                '{}/@search?portal_type=opengever.document.document&'
                'portal_type=ftw.mail.mail&metadata_fields=UID&'
                'metadata_fields=filename'.format(
                    self.workspace.absolute_url()))
            self.assertEqual(expected_url, documents['@id'])
            self.assertEqual(1, documents['items_total'])
            self.assertEqual(
                {u'@id': document.absolute_url(),
                 u'@type': u'opengever.document.document',
                 u'UID': document.UID(),
                 u'description': u'',
                 u'filename': u'',
                 u'review_state': u'document-state-draft',
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
                    manager.copy_document_from_workspace(
                        self.workspace.UID(), document.UID())

            self.assertEqual(1, len(children['added']))
            workspace_document = children['added'].pop()
            self.assertEqual(document.title, workspace_document.title)
            self.assertEqual(document.description, workspace_document.description)
            self.assertEqual(document.file.open().read(),
                             workspace_document.file.open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(document),
                manager._serialized_document_schema_fields(workspace_document))

    def test_copy_document_without_file_from_a_workspace(self):
        document = create(Builder('document')
                          .within(self.workspace))
        transaction.commit()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            with self.observe_children(self.dossier) as children:
                with auto_commit_after_request(manager.client):
                    manager.copy_document_from_workspace(
                        self.workspace.UID(), document.UID())

            self.assertEqual(1, len(children['added']))
            workspace_document = children['added'].pop()
            self.assertEqual(document.title, workspace_document.title)
            self.assertEqual(document.description, workspace_document.description)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(document),
                manager._serialized_document_schema_fields(workspace_document))

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
                    manager.copy_document_from_workspace(
                        self.workspace.UID(), mail.UID())

            self.assertEqual(1, len(children['added']))
            workspace_mail = children['added'].pop()
            self.assertEqual(mail.title, workspace_mail.title)
            self.assertEqual(mail.description, workspace_mail.description)
            self.assertEqual(workspace_mail.get_file().open().read(),
                             mail.get_file().open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))

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
                    manager.copy_document_from_workspace(
                        self.workspace.UID(), mail.UID())

            self.assertEqual(1, len(children['added']))
            workspace_mail = children['added'].pop()
            self.assertEqual(mail.title, workspace_mail.title)
            self.assertEqual(mail.description, workspace_mail.description)
            self.assertEqual(workspace_mail.get_file().open().read(),
                             mail.get_file().open().read())

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))
