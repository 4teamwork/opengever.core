from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import HTTPServerError
from opengever.base.command import CreateEmailCommand
from opengever.base.oguid import Oguid
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.locking.lock import LOCK_TYPE_COPIED_TO_WORKSPACE_LOCK
from opengever.mail.tests import MAIL_DATA
from opengever.testing.assets import load
from opengever.workspace.participation import WORKSPCAE_GUEST
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from opengever.workspaceclient.exceptions import WorkspaceNotLinked
from opengever.workspaceclient.interfaces import ILinkedDocuments
from opengever.workspaceclient.interfaces import ILinkedToWorkspace
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.linked_workspaces import RETRIEVAL_MODE_COPY
from opengever.workspaceclient.linked_workspaces import RETRIEVAL_MODE_VERSION
from opengever.workspaceclient.storage import LinkedWorkspacesStorage
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from plone.locking.interfaces import ILockable
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
import json
import requests_mock
import transaction


def fix_publisher_test_bug(browser, obj):
    # We need to make a GET request before using a post-endpoint.
    # This is a workaround to fix a weird issue where we get
    # a silent `ConflictError`. ZPublisher will then automatically
    # republish the request although the previous POST request has
    # already been handled successfully, effectively creating the new
    # workspace twice
    #
    # If we get the dossier first, before performing a post request, it seems
    # to work properly.
    #
    # This issue only appears in a testing environment.
    browser.open(obj, method='GET', headers={'Accept': 'application/json'})


@contextmanager
def auto_commit_after_removing_dossier_reference(client):
    """This contextmanager injects a session hook for the current client
    session to commit the transaction after removing the dossier reference.
    This is necessary because otherwise a ConflictError will be thrown
    if the dossier and the workspace are modified at the same time.

    This issue only appears in a testing environment.
    """
    def commit_after_removing_dossier_reference(r, *args, **kwargs):
        if '@remove-dossier-reference' in r.url:
            transaction.commit()

    client_session_hooks = client.session.session.hooks
    original_hooks = list(client_session_hooks['response'])
    client_session_hooks['response'].append(commit_after_removing_dossier_reference)

    try:
        yield
    finally:
        client_session_hooks['response'] = original_hooks


class TestLinkedWorkspacesPost(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_create_linked_workspace(self, browser):
        browser.login()
        with self.observe_children(self.workspace_root) as children:
            with self.workspace_client_env():
                fix_publisher_test_bug(browser, self.dossier)

                # This prevents a database conflict error,
                # otherwise both the dossier and the workspace will be modified.
                # This is a testing issue (doesn't happen in production)
                alsoProvides(self.dossier, ILinkedToWorkspace)
                transaction.commit()

                browser.open(
                    self.dossier.absolute_url() + '/@create-linked-workspace',
                    data=json.dumps({"title": "My linked workspace"}),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual(200, browser.status_code)

        # Because of test setup which contains GEVER and teamraum in the same
        # plone deployment, a conflict error leads to a doubled workspace
        # creation. This happens only in testing environment and can therefore
        # be ignored.
        self.assertIn(browser.json.get('@id'),
                      [aa.absolute_url() for aa in children['added']])

        linked_workspace = children['added'].pop()
        self.assertEqual(browser.json.get('title'),
                         linked_workspace.title)
        dossier_oguid = Oguid.for_object(self.dossier).id
        expected_gever_url = '{}/@resolve-oguid?oguid={}'.format(
            api.portal.get().absolute_url(), dossier_oguid)
        self.assertEqual(browser.json.get('external_reference'), dossier_oguid)
        self.assertEqual(expected_gever_url, linked_workspace.gever_url)

    @browsing
    def test_raise_not_found_if_feature_is_not_activated(self, browser):
        browser.login()
        self.enable_feature(enabled=False)

        browser.exception_bubbling = True
        with self.assertRaises(NotFound):
            browser.open(
                self.dossier.absolute_url() + '/@create-linked-workspace',
                data=json.dumps({"title": "My linked workspace"}),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )

    @browsing
    def test_create_linked_workspace_raises_unauthorized_if_dossier_is_closed(self, browser):
        browser.login()
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            browser.open(self.expired_dossier, view='/@create-linked-workspace',
                         data=json.dumps({"title": "My linked workspace"}),
                         method='POST',
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

    @browsing
    def test_only_workspace_client_users_can_use_the_api(self, browser):
        browser.exception_bubbling = True
        browser.login()
        with self.workspace_client_env():
            roles = set(api.user.get_roles())
            self.grant(roles.difference({'WorkspaceClientUser'}))
            with self.assertRaises(Unauthorized):
                browser.open(
                    self.dossier.absolute_url() + '/@create-linked-workspace',
                    data=json.dumps({"title": "My linked workspace"}),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

    @browsing
    def test_raise_exception_for_subdossiers(self, browser):
        subdossier = create(Builder('dossier').within(self.dossier))
        transaction.commit()
        browser.login()
        with self.workspace_client_env():
            fix_publisher_test_bug(browser, subdossier)

            browser.exception_bubbling = True
            with self.assertRaises(BadRequest):
                browser.open(
                    subdossier.absolute_url() + '/@create-linked-workspace',
                    data=json.dumps({"title": "My linked workspace"}),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )


class TestLinkToWorkspacesPost(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_link_to_workspace(self, browser):
        browser.login()
        with self.workspace_client_env():
            fix_publisher_test_bug(browser, self.dossier)

            # This prevents a database conflict error,
            # otherwise both the dossier and the workspace will be modified.
            # This is a testing issue (doesn't happen in production)
            alsoProvides(self.dossier, ILinkedToWorkspace)
            transaction.commit()

            browser.open(
                self.dossier.absolute_url() + '/@link-to-workspace',
                data=json.dumps({"workspace_uid": self.workspace.UID()}),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})

        self.assertEqual(204, browser.status_code)
        dossier_oguid = Oguid.for_object(self.dossier).id
        expected_gever_url = '{}/@resolve-oguid?oguid={}'.format(
            api.portal.get().absolute_url(), dossier_oguid)

        self.assertEqual(dossier_oguid, self.workspace.external_reference)
        self.assertEqual(expected_gever_url, self.workspace.gever_url)

    @browsing
    def test_raises_not_found_if_workspaceclient_feature_not_enabled(self, browser):
        browser.login()
        self.enable_feature(enabled=False)

        browser.exception_bubbling = True
        with self.assertRaises(NotFound):
            browser.open(
                self.dossier.absolute_url() + '/@link-to-workspace',
                data=json.dumps({"workspace_uid": self.workspace.UID()}),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})

    @browsing
    def test_link_to_workspace_raises_unauthorized_if_dossier_is_closed(self, browser):
        browser.login()
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            browser.open(self.expired_dossier, view='/@link-to-workspace',
                         data=json.dumps({"workspace_uid": self.workspace.UID()}),
                         method='POST',
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json'})

    @browsing
    def test_missing_workspace_uid_raises_bad_request(self, browser):
        browser.exception_bubbling = True
        with self.workspace_client_env():
            browser.login()
            fix_publisher_test_bug(browser, self.dossier)
            with self.assertRaises(BadRequest) as cm:
                browser.open(
                    self.dossier.absolute_url() + '/@link-to-workspace',
                    data=json.dumps({}),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'})
        self.assertEqual('workspace_uid_required', str(cm.exception))

    @browsing
    def test_only_workspace_client_users_can_use_the_api(self, browser):
        browser.exception_bubbling = True
        browser.login()
        with self.workspace_client_env():
            roles = set(api.user.get_roles())
            self.grant(roles.difference({'WorkspaceClientUser'}))
            with self.assertRaises(Unauthorized):
                browser.open(
                    self.dossier.absolute_url() + '/@link-to-workspace',
                    data=json.dumps({"workspace_uid": self.workspace.UID()}),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'})

    @browsing
    def test_raise_exception_for_subdossiers(self, browser):
        subdossier = create(Builder('dossier').within(self.dossier))
        transaction.commit()
        browser.login()
        with self.workspace_client_env():
            fix_publisher_test_bug(browser, subdossier)

            browser.exception_bubbling = True
            with self.assertRaises(BadRequest):
                browser.open(
                    subdossier.absolute_url() + '/@link-to-workspace',
                    data=json.dumps({"workspace_uid": self.workspace.UID()}),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'})


class TestLinkedWorkspacesGet(FunctionalWorkspaceClientTestCase):
    @browsing
    def test_get_linked_workspaces(self, browser):
        with self.workspace_client_env():
            browser.login()
            response = browser.open(
                self.dossier.absolute_url() + '/@linked-workspaces',
                method='GET', headers={'Accept': 'application/json'}).json

            self.assertEqual([], response.get('items'))

            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            transaction.commit()

            response = browser.open(
                self.dossier.absolute_url() + '/@linked-workspaces',
                method='GET', headers={'Accept': 'application/json'}).json

            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in response.get('items')])

            self.assertFalse(response['workspaces_without_view_permission'])

    @browsing
    def test_workspaces_without_view_permission(self, browser):
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add('a_workspace_uid')
            transaction.commit()

            browser.login()
            response = browser.open(
                self.dossier.absolute_url() + '/@linked-workspaces',
                method='GET', headers={'Accept': 'application/json'}).json

            self.assertTrue(response['workspaces_without_view_permission'])

    @browsing
    def test_get_linked_workspaces_replaces_service_url_with_actual_request_url(self, browser):
        url = self.dossier.absolute_url() + '/@linked-workspaces'
        with self.workspace_client_env():
            browser.login()
            response = browser.open(url, method='GET', headers={'Accept': 'application/json'}).json

            self.assertEqual(url, response.get('@id'))

    @browsing
    def test_get_linked_workspaces_handles_batching(self, browser):
        endpoint_url = self.dossier.absolute_url() + '/@linked-workspaces'
        query_url = endpoint_url + '?b_size=1'
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())

            workspace2 = create(Builder('workspace').within(self.workspace_root))
            self.grant('WorkspaceMember', on=workspace2)
            manager.storage.add(workspace2.UID())

            transaction.commit()

            browser.login()
            response = browser.open(
                query_url,
                method='GET',
                headers={'Accept': 'application/json'}).json

            self.assertEqual(endpoint_url, response.get('@id'))
            self.assertEqual(2, response.get('items_total'))
            self.assertEqual(
                {"@id": query_url,
                 "first": endpoint_url + '?b_start=0&b_size=1',
                 "last": endpoint_url + '?b_start=1&b_size=1',
                 "next": endpoint_url + '?b_start=1&b_size=1'},
                response.get('batching'))

            self.assertEqual(1, len(response.get('items')))
            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in response.get('items')])

    @browsing
    def test_lists_workspaces_for_main_dossier_when_called_on_subdossier(self, browser):
        manager = ILinkedWorkspaces(self.dossier)
        manager.storage.add(self.workspace.UID())

        subdossier = create(Builder('dossier').within(self.dossier))
        transaction.commit()

        browser.login()

        with self.workspace_client_env():
            response = browser.open(
                subdossier.absolute_url() + '/@linked-workspaces',
                method='GET', headers={'Accept': 'application/json'}).json

        self.assertEqual(
            [self.workspace.absolute_url()],
            [workspace.get('@id') for workspace in response.get('items')])

        self.assertFalse(response['workspaces_without_view_permission'])

    @browsing
    def test_request_error_handling(self, browser):
        LinkedWorkspacesStorage(self.dossier).add(self.workspace.UID())

        def assertStatusCode(test_with, raised_error):
            with self.workspace_client_env():
                browser.login()
                browser.exception_bubbling = True
                with requests_mock.Mocker() as mocker:
                    mocker.post('{}/@@oauth2-token'.format(self.portal.absolute_url()),
                                status_code=test_with)

                    with self.assertRaises(HTTPServerError):
                        browser.open(
                            self.dossier.absolute_url() + '/@linked-workspaces',
                            method='GET', headers={'Accept': 'application/json'}).json

            self.assertEqual(
                raised_error, browser.status_code,
                '{} should raise a {}'.format(test_with, raised_error))
            self.assertEqual(
                test_with, browser.json.get('service_error').get('status_code'),
                'The service_error status code should contain the original status code')

        assertStatusCode(test_with=404, raised_error=502)
        assertStatusCode(test_with=408, raised_error=504)
        assertStatusCode(test_with=500, raised_error=502)
        assertStatusCode(test_with=502, raised_error=502)
        assertStatusCode(test_with=504, raised_error=504)


class TestUnlinkWorkspacePost(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_unlink_workspace(self, browser):
        browser.login()
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.open(self.dossier, view='@linked-workspaces',
                         method='GET', headers={'Accept': 'application/json'})

            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in browser.json['items']])

            with auto_commit_after_removing_dossier_reference(manager.client):
                browser.open(
                    self.dossier, view='@unlink-workspace',
                    data=json.dumps({'workspace_uid': self.workspace.UID()}),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'})

            browser.open(self.dossier, view='@linked-workspaces', method='GET',
                         headers={'Accept': 'application/json'})

            self.assertEqual([], browser.json['items'])

    @browsing
    def test_unlink_workspace_and_deactivate_workspace(self, browser):
        self.grant('WorkspaceAdmin', on=self.workspace)
        browser.login()
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.open(self.dossier, view='@linked-workspaces', method='GET',
                         headers={'Accept': 'application/json'})

            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in browser.json['items']])
            self.assertEqual('opengever_workspace--STATUS--active',
                             api.content.get_state(self.workspace))

            with auto_commit_after_removing_dossier_reference(manager.client):
                browser.open(self.dossier, view='@unlink-workspace', method='POST',
                             data=json.dumps({'workspace_uid': self.workspace.UID(),
                                             'deactivate_workspace': True}),
                             headers={'Accept': 'application/json',
                                      'Content-Type': 'application/json'})

            browser.open(self.dossier, view='@linked-workspaces',
                         method='GET', headers={'Accept': 'application/json'})

            self.assertEqual([], browser.json['items'])
            self.assertEqual('opengever_workspace--STATUS--inactive',
                             api.content.get_state(self.workspace))

    @browsing
    def test_unlink_workspace_also_when_deactivation_fails(self, browser):
        browser.login()
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.open(self.dossier, view='@linked-workspaces', method='GET',
                         headers={'Accept': 'application/json'})

            self.assertEqual(
                [self.workspace.absolute_url()],
                [workspace.get('@id') for workspace in browser.json['items']])

            with auto_commit_after_removing_dossier_reference(manager.client):
                with browser.expect_http_error(400):
                    browser.open(
                        self.dossier, view='@unlink-workspace',
                        data=json.dumps({'workspace_uid': self.workspace.UID(),
                                         'deactivate_workspace': True}),
                        method='POST',
                        headers={'Accept': 'application/json',
                                 'Content-Type': 'application/json'})

            self.assertEqual({
                u'type': u'BadRequest', u'additional_metadata': {},
                u'translated_message': u'The workspace was unlinked, but it could not be deactivated.',
                u'message': u'deactivate_workspace_failed'},
                browser.json)

            browser.open(self.dossier, view='@linked-workspaces', method='GET',
                         headers={'Accept': 'application/json'})
            self.assertEqual([], browser.json['items'])


class TestCopyDocumentToWorkspacePost(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_raises_when_workspace_uid_missing(self, browser):
        document = create(Builder('document').within(self.dossier))

        payload = {
            'document_uid': document.UID()
        }

        with self.workspace_client_env():
            browser.login()

            browser.exception_bubbling = True
            with self.assertRaises(BadRequest) as cm:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )
        self.assertEqual('workspace_uid_required', str(cm.exception))

    @browsing
    def test_raises_when_document_uid_missing(self, browser):
        payload = {
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            browser.login()

            browser.exception_bubbling = True
            with self.assertRaises(BadRequest) as cm:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual("Property 'document_uid' is required", str(cm.exception))

    @browsing
    def test_raises_when_document_cant_be_looked_up_by_uid(self, browser):
        payload = {
            'document_uid': 'not-existing-document-uid',
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            browser.login()

            browser.exception_bubbling = True
            with self.assertRaises(BadRequest) as cm:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual("The document does not exist", str(cm.exception))

    @browsing
    def test_raises_when_document_is_not_within_the_main_dossier(self, browser):
        sister_dossier = create(Builder('dossier').within(self.leaf_repofolder))
        document = create(Builder('document').within(sister_dossier))

        payload = {
            'document_uid': document.UID(),
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            browser.login()

            browser.exception_bubbling = True
            with self.assertRaises(BadRequest) as cm:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual("Only documents within the current main dossier are allowed", str(cm.exception))

    @browsing
    def test_raise_exception_for_subdossiers(self, browser):
        subdossier = create(Builder('dossier').within(self.dossier))
        document = create(Builder('document')
                          .within(self.dossier)
                          .having(preserved_as_paper=True))

        payload = {
            'document_uid': document.UID(),
            'workspace_uid': self.workspace.UID(),
        }

        transaction.commit()
        browser.login()

        with self.workspace_client_env():
            browser.exception_bubbling = True
            with self.assertRaises(BadRequest):
                browser.open(
                    subdossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

    @browsing
    def test_copy_document_without_file_to_workspace(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .having(preserved_as_paper=True))

        payload = {
            'document_uid': document.UID(),
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            with self.observe_children(self.workspace) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            self.assertEqual(len(children['added']), 1)

            id_ = browser.json['id'].encode('ascii')
            workspace_document = self.workspace.restrictedTraverse(id_)

            self.assertEqual(workspace_document.absolute_url(), browser.json.get('@id'))

            # Documents without file are not linked to GEVER documents when
            # copied to Teamraum, since there's no file that could be
            # transferred back.
            self.assertIsNone(
                ILinkedDocuments(workspace_document).linked_gever_document)

            self.assertEqual(
                [],
                ILinkedDocuments(document).linked_workspace_documents)

            self.assertEqual(u'', IDocumentMetadata(workspace_document).gever_url)

    @browsing
    def test_copy_document_with_file_to_a_workspace(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .with_dummy_content())

        payload = {
            'document_uid': document.UID(),
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, document)
            with self.observe_children(self.workspace) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            # XXX: This is incorrect, only one document should be added. This
            # is a testing issue (doesn't happen in production) that was never
            # really addressed. The fix_publisher_test_bug() is supposed to
            # work around this, but it doesn't.
            self.assertEqual(len(children['added']), 2)

            id_ = browser.json['id'].encode('ascii')
            workspace_document = self.workspace.restrictedTraverse(id_)

            self.assertEqual(workspace_document.absolute_url(), browser.json.get('@id'))
            self.assertEqual(workspace_document.title, document.title)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(document),
                manager._serialized_document_schema_fields(workspace_document))

            self.assertEqual(
                {'UID': IUUID(document)},
                ILinkedDocuments(workspace_document).linked_gever_document)

            expected_gever_url = '{}/@resolve-oguid?oguid={}'.format(
                api.portal.get().absolute_url(), Oguid.for_object(document).id)
            self.assertEqual(expected_gever_url, IDocumentMetadata(workspace_document).gever_url)

            # XXX: Because of the way these tests works, setting of the link
            # to the workspace documents on this GEVER document happens in
            # another transaction and doesn't seem to propagate back where
            # it can be seen in this one. On a real deployment, links are are
            # added on both sides.
            # self.assertEqual(
            #     [{'UID': IUUID(workspace_document)}],
            #     ILinkedDocuments(document).linked_workspace_documents)

    @browsing
    def test_copy_eml_mail_to_a_workspace(self, browser):
        mail = create(Builder("mail")
                      .with_message(MAIL_DATA)
                      .within(self.dossier))
        transaction.commit()

        payload = {
            'document_uid': mail.UID(),
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, mail)
            with self.observe_children(self.workspace) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            # XXX: This is incorrect, only one document should be added. This
            # is a testing issue (doesn't happen in production) that was never
            # really addressed. The fix_publisher_test_bug() is supposed to
            # work around this, but it doesn't.
            self.assertEqual(len(children['added']), 2)

            id_ = browser.json['id'].encode('ascii')
            workspace_mail = self.workspace.restrictedTraverse(id_)

            self.assertEqual(workspace_mail.absolute_url(), browser.json.get('@id'))
            self.assertEqual(workspace_mail.title, mail.title)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))

            self.assertEqual(
                {'UID': IUUID(mail)},
                ILinkedDocuments(workspace_mail).linked_gever_document)

            expected_gever_url = '{}/@resolve-oguid?oguid={}'.format(
                api.portal.get().absolute_url(), Oguid.for_object(mail).id)
            self.assertEqual(expected_gever_url, IDocumentMetadata(workspace_mail).gever_url)

            # XXX: Because of the way these tests works, setting of the link
            # to the workspace documents on this GEVER document happens in
            # another transaction and doesn't seem to propagate back where
            # it can be seen in this one. On a real deployment, links are are
            # added on both sides.
            # self.assertEqual(
            #     [{'UID': IUUID(workspace_mail)}],
            #     ILinkedDocuments(mail).linked_workspace_documents)

    @browsing
    def test_copy_msg_mail_to_a_workspace(self, browser):
        msg = load('testmail.msg')
        command = CreateEmailCommand(
            self.dossier, 'testm\xc3\xa4il.msg', msg)
        mail = command.execute()
        transaction.commit()

        payload = {
            'document_uid': mail.UID(),
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, mail)
            with self.observe_children(self.workspace) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            # XXX: This is incorrect, only one document should be added. This
            # is a testing issue (doesn't happen in production) that was never
            # really addressed. The fix_publisher_test_bug() is supposed to
            # work around this, but it doesn't.
            self.assertEqual(len(children['added']), 2)

            id_ = browser.json['id'].encode('ascii')
            workspace_mail = self.workspace.restrictedTraverse(id_)

            self.assertEqual(workspace_mail.absolute_url(), browser.json.get('@id'))
            self.assertEqual(workspace_mail.title, mail.title)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(workspace_mail))

            self.assertEqual(
                {'UID': IUUID(mail)},
                ILinkedDocuments(workspace_mail).linked_gever_document)

            # XXX: Because of the way these tests works, setting of the link
            # to the workspace documents on this GEVER document happens in
            # another transaction and doesn't seem to propagate back where
            # it can be seen in this one. On a real deployment, links are are
            # added on both sides.
            # self.assertEqual(
            #     [{'UID': IUUID(workspace_mail)}],
            #     ILinkedDocuments(mail).linked_workspace_documents)

    @browsing
    def test_copy_document_to_workspace_is_prevented_if_checked_out(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .with_dummy_content())

        manager = getMultiAdapter((document, self.request), ICheckinCheckoutManager)
        manager.checkout()

        payload = {
            'document_uid': document.UID(),
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, document)
            with self.observe_children(self.workspace) as children:
                with browser.expect_http_error(code=400):
                    browser.open(
                        self.dossier.absolute_url() + '/@copy-document-to-workspace',
                        data=json.dumps(payload),
                        method='POST',
                        headers={'Accept': 'application/json',
                                 'Content-Type': 'application/json'},
                    )

            self.assertEqual(len(children['added']), 0)
            self.assertEqual(
                {u'type': u'BadRequest',
                 u'message': u"Document can't be copied to a workspace "
                             u"because it's currently checked out"},
                browser.json)

    @browsing
    def test_lock_document_when_copying_to_a_workspace(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .with_dummy_content())

        payload = {
            'document_uid': document.UID(),
            'workspace_uid': self.workspace.UID(),
            'lock': True,
        }

        lockable = ILockable(document)
        self.assertFalse(lockable.locked())

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, document)
            with self.observe_children(self.workspace) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        # XXX: This is incorrect, only one document should be added. This
        # is a testing issue (doesn't happen in production) that was never
        # really addressed. The fix_publisher_test_bug() is supposed to
        # work around this, but it doesn't.
        self.assertEqual(len(children['added']), 2)

        self.assertTrue(lockable.locked())
        self.assertEqual(1, len(lockable.lock_info()))
        self.assertEqual(LOCK_TYPE_COPIED_TO_WORKSPACE_LOCK,
                         lockable.lock_info()[0]['type'].__name__)

    @browsing
    def test_also_allows_copying_documents_to_workspace_folder(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .with_dummy_content())

        folder = create(Builder('workspace folder')
                        .within(self.workspace))

        payload = {
            'document_uid': document.UID(),
            'workspace_uid': self.workspace.UID(),
            'folder_uid': folder.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, document)
            with self.observe_children(folder) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            # XXX: This is incorrect, only one document should be added. This
            # is a testing issue (doesn't happen in production) that was never
            # really addressed. The fix_publisher_test_bug() is supposed to
            # work around this, but it doesn't.
            self.assertEqual(len(children['added']), 2)

            id_ = browser.json['id'].encode('ascii')
            workspace_document = folder.restrictedTraverse(id_)

            self.assertEqual(workspace_document.absolute_url(), browser.json.get('@id'))
            self.assertEqual(workspace_document.title, document.title)

            self.assertEqual(
                {'UID': IUUID(document)},
                ILinkedDocuments(workspace_document).linked_gever_document)


class TestPrepareCopyDossierToWorkspaceValidation(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_passes_if_all_ok(self, browser):
        payload = {
            'validate_only': True,
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            browser.open(
                self.dossier.absolute_url() + '/@prepare-copy-dossier-to-workspace',
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers,
            )
        self.assertEqual({u'ok': True}, browser.json)
        self.assertEqual(200, browser.status_code)

    @browsing
    def test_fails_if_workspace_uid_missing(self, browser):
        payload = {
            'validate_only': True,
        }

        with self.workspace_client_env():
            browser.login()

            with browser.expect_http_error(code=400):
                browser.open(
                    self.dossier.absolute_url() + '/@prepare-copy-dossier-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers=self.api_headers,
                )
        expected = {
            'type': 'BadRequest',
            'message': 'workspace_uid_required',
            'translated_message': "Property 'workspace_uid' is required",
            'additional_metadata': {},
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_fails_if_workspace_not_linked(self, browser):
        payload = {
            'validate_only': True,
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            browser.login()

            with browser.expect_http_error(code=400):
                browser.open(
                    self.dossier.absolute_url() + '/@prepare-copy-dossier-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers=self.api_headers,
                )
        expected = {
            'errors': [{
                'translated_message': 'Main dossier not linked to workspace',
                'message': 'main_dossier_not_linked_to_workspace',
                'additional_metadata': {
                    'obj_title': 'My dossier',
                    'obj_type': 'opengever.dossier.businesscasedossier',
                    'obj_uid': self.dossier.UID(),
                    'obj_url': self.dossier.absolute_url(),
                },
            }],
            'ok': False,
        }
        self.assertEqual(expected, browser.json)
        self.assertEqual(400, browser.status_code)

    @browsing
    def test_fails_if_dossier_contains_checked_out_doc(self, browser):
        payload = {
            'validate_only': True,
            'workspace_uid': self.workspace.UID(),
        }

        document = create(Builder('document')
                          .within(self.dossier)
                          .checked_out())

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()

            with browser.expect_http_error(code=400):
                browser.open(
                    self.dossier.absolute_url() + '/@prepare-copy-dossier-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers=self.api_headers,
                )
        expected = {
            'errors': [{
                'translated_message': 'Document is checked out',
                'message': 'document_is_checked_out',
                'additional_metadata': {
                    'obj_title': u'Testdokum\xe4nt',
                    'obj_type': 'opengever.document.document',
                    'obj_uid': document.UID(),
                    'obj_url': document.absolute_url(),
                },
            }],
            'ok': False,
        }
        self.assertEqual(expected, browser.json)
        self.assertEqual(400, browser.status_code)


class TestPrepareCopyDossierToWorkspaceStructureCreation(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_creates_structure(self, browser):
        payload = {
            'validate_only': False,
            'workspace_uid': self.workspace.UID(),
        }

        document = create(Builder('document')
                          .within(self.dossier))

        subdossier = create(Builder('dossier')
                            .titled(u'Subdossier')
                            .within(self.dossier))

        subdocument = create(Builder('document')
                             .titled(u'Subdocument')
                             .within(subdossier))
        self.commit_solr()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            with self.observe_children(self.workspace) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@prepare-copy-dossier-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers=self.api_headers,
                )

            self.assertEqual(
                1, len(children['added']),
                'Workspace should have 1 direct new folder')

            folder = list(children['added'])[0]

            self.assertEqual(1, len(folder.objectValues()))
            subfolder = folder.objectValues()[0]

            self.assertEqual(u'My dossier', folder.title)
            self.assertEqual(u'Subdossier', subfolder.title)

        expected = {
            'docs_to_upload': [
                {
                    'source_document_uid': document.UID(),
                    'target_folder_uid': folder.UID(),
                    'title': u'Testdokum\xe4nt',
                },
                {
                    'source_document_uid': subdocument.UID(),
                    'target_folder_uid': subfolder.UID(),
                    'title': u'Subdocument',
                },
            ]
        }
        self.assertEqual(expected, browser.json)
        self.assertEqual(200, browser.status_code)

    @browsing
    def test_also_creates_folders_for_empty_dossiers(self, browser):
        payload = {
            'validate_only': False,
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            with self.observe_children(self.workspace) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@prepare-copy-dossier-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers=self.api_headers,
                )

            self.assertEqual(
                1, len(children['added']),
                'Workspace should have 1 direct new folder')

        expected = {
            'docs_to_upload': []
        }
        self.assertEqual(expected, browser.json)
        self.assertEqual(200, browser.status_code)

    @browsing
    def test_maps_documents_in_non_dossiers_to_closest_containing_dossier(self, browser):
        payload = {
            'validate_only': False,
            'workspace_uid': self.workspace.UID(),
        }

        task = create(Builder('task')
                      .titled(u'Task')
                      .within(self.dossier))

        document = create(Builder('document')
                          .within(task))

        self.commit_solr()

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            with self.observe_children(self.workspace) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@prepare-copy-dossier-to-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers=self.api_headers,
                )

            self.assertEqual(
                1, len(children['added']),
                'Workspace should have 1 direct new folder')

            folder = list(children['added'])[0]

        expected = {
            'docs_to_upload': [
                {
                    'source_document_uid': document.UID(),
                    'target_folder_uid': folder.UID(),
                    'title': u'Testdokum\xe4nt',
                },
            ]
        }
        self.assertEqual(expected, browser.json)
        self.assertEqual(200, browser.status_code)


class TestListDocumentsInLinkedWorkspaceGet(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_raises_when_workspace_uid_is_missing(self, browser):

        url = "/".join([self.dossier.absolute_url(),
                        '@list-documents-in-linked-workspace',
                        ])

        with self.workspace_client_env():
            browser.login()
            browser.exception_bubbling = True
            with self.assertRaises(BadRequest) as cm:
                browser.open(
                    url,
                    method='GET',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual("Missing path segment 'workspace_uid'",
                         str(cm.exception))

    @browsing
    def test_raises_when_workspace_cant_be_looked_up_by_uid(self, browser):

        url = "/".join([self.dossier.absolute_url(),
                        '@list-documents-in-linked-workspace',
                        'nonexisting'])

        with self.workspace_client_env():
            browser.login()
            browser.exception_bubbling = True
            with self.assertRaises(WorkspaceNotLinked) as cm:
                browser.open(
                    url,
                    method='GET',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual(
            "The workspace in not linked with the current dossier.",
            str(cm.exception))

    @browsing
    def test_lists_documents_in_linked_workspace(self, browser):
        document = create(Builder('document').within(self.workspace))

        url = "/".join([self.dossier.absolute_url(),
                        '@list-documents-in-linked-workspace',
                        str(self.workspace.UID())])

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()

            response = browser.open(
                    url,
                    method='GET',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                ).json

            self.assertEqual(url, response.get('@id'))
            self.assertEqual(1, response.get('items_total'))
            self.assertEqual(
                [{u'@id': document.absolute_url(),
                  u'@type': u'opengever.document.document',
                  u'UID': document.UID(),
                  u'checked_out': u'',
                  u'description': u'',
                  u'file_extension': u'',
                  u'filename': u'',
                  u'is_leafnode': None,
                  u'review_state': u'opengever_workspace_document--STATUS--active',
                  u'title': u'Testdokum\xe4nt'}],
                response['items'])

    @browsing
    def test_lists_documents_in_linked_workspace_handles_batching(self, browser):
        document1 = create(Builder('document').within(self.workspace))
        create(Builder('document').within(self.workspace))

        endpoint_url = "/".join([self.dossier.absolute_url(),
                                 '@list-documents-in-linked-workspace',
                                 str(self.workspace.UID())])
        query_url = endpoint_url + '?b_size=1'
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            response = browser.open(
                    query_url,
                    method='GET',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                ).json

            self.assertEqual(endpoint_url, response.get('@id'))
            self.assertEqual(2, response.get('items_total'))
            self.assertEqual(
                {"@id": query_url,
                 "first": endpoint_url + '?b_start=0&b_size=1',
                 "last": endpoint_url + '?b_start=1&b_size=1',
                 "next": endpoint_url + '?b_start=1&b_size=1'},
                response.get('batching'))

            self.assertEqual(1, len(response.get('items')))
            self.assertEqual(
                [document1.absolute_url()],
                [document.get('@id') for document in response.get('items')])


class TestCopyDocumentFromWorkspacePost(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_raises_when_document_uid_missing(self, browser):
        payload = {
            'workspace_uid': self.workspace.UID(),
        }

        with self.workspace_client_env():
            browser.login()

            browser.exception_bubbling = True
            with self.assertRaises(BadRequest) as cm:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual("Property 'document_uid' is required", str(cm.exception))

    @browsing
    def test_raises_when_workspace_uid_missing(self, browser):
        document = create(Builder('document').within(self.workspace))
        payload = {
            'document_uid': document.UID()
        }

        with self.workspace_client_env():
            browser.login()

            browser.exception_bubbling = True
            with self.assertRaises(BadRequest) as cm:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )
        self.assertEqual('workspace_uid_required', str(cm.exception))

    @browsing
    def test_raises_when_document_cant_be_looked_up_by_uid(self, browser):
        payload = {
            'workspace_uid': self.workspace.UID(),
            'document_uid': 'not-existing-document-uid',
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()

            with browser.expect_http_error(400):
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            self.assertEqual(
                {u'additional_metadata': {},
                 u'message': u'Document not in linked workspace',
                 u'translated_message': u'Document is not in a linked workspace.',
                 u'type': u'BadRequest'},
                browser.json)

    @browsing
    def test_raises_when_document_is_not_within_linked_workspace(self, browser):
        document = create(Builder('document').within(self.dossier))

        payload = {
            'workspace_uid': self.workspace.UID(),
            'document_uid': document.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()

            with browser.expect_http_error(400):
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            self.assertEqual(
                {u'additional_metadata': {},
                 u'message': u'Document not in linked workspace',
                 u'translated_message': u'Document is not in a linked workspace.',
                 u'type': u'BadRequest'},
                browser.json)

    @browsing
    def test_copy_document_without_file_from_workspace(self, browser):
        document = create(Builder('document')
                          .within(self.workspace)
                          .having(preserved_as_paper=True))

        payload = {
            'workspace_uid': self.workspace.UID(),
            'document_uid': document.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            with self.observe_children(self.dossier) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            self.assertEqual(len(children['added']), 1)
            document_copy = children['added'].pop()
            self.assertEqual(document_copy.absolute_url(), browser.json.get('@id'))
            self.assertEqual(
                RETRIEVAL_MODE_COPY,
                browser.json.get('teamraum_connect_retrieval_mode'))

    @browsing
    def test_copy_document_with_file_from_a_workspace(self, browser):
        document = create(Builder('document')
                          .within(self.workspace)
                          .with_dummy_content())

        payload = {
            'workspace_uid': self.workspace.UID(),
            'document_uid': document.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, document)
            with self.observe_children(self.dossier) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            self.assertEqual(len(children['added']), 1)
            document_copy = children['added'].pop()

            self.assertEqual(document_copy.absolute_url(), browser.json.get('@id'))
            self.assertEqual(document_copy.title, document.title)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(document),
                manager._serialized_document_schema_fields(document_copy))

            self.assertEqual(
                RETRIEVAL_MODE_COPY,
                browser.json.get('teamraum_connect_retrieval_mode'))

    @browsing
    def test_copy_document_from_workspace_as_new_version(self, browser):
        gever_doc = create(Builder('document')
                           .within(self.dossier)
                           .with_dummy_content())

        self.assertIsNone(Versioner(gever_doc).get_current_version_id())
        self.assertFalse(Versioner(gever_doc).has_initial_version())

        initial_content = gever_doc.file.data
        initial_filename = gever_doc.file.filename

        self.assertEqual('Test data', initial_content)
        self.assertEqual(u'Testdokumaent.doc', initial_filename)

        new_content = 'Content produced in Workspace'
        new_filename = u'workspace.doc'

        workspace_doc = create(Builder('document')
                               .within(self.workspace)
                               .having(gever_url=u'url')
                               .attach_file_containing(new_content,
                                                       name=new_filename))

        ILinkedDocuments(workspace_doc).link_gever_document(IUUID(gever_doc))
        ILinkedDocuments(gever_doc).link_workspace_document(IUUID(workspace_doc))
        self.assertEqual(u'url', IDocumentMetadata(workspace_doc).gever_url)

        payload = {
            'workspace_uid': IUUID(self.workspace),
            'document_uid': IUUID(workspace_doc),
            'as_new_version': True,
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, workspace_doc)
            with self.observe_children(self.dossier) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            self.assertEqual(len(children['added']), 0)

            self.assertTrue(Versioner(gever_doc).has_initial_version())
            self.assertEqual(1, Versioner(gever_doc).get_current_version_id())

            self.assertEqual(new_content, gever_doc.file.data)
            self.assertEqual(initial_filename, gever_doc.file.filename)

            initial_version = Versioner(gever_doc).retrieve(0)
            initial_version_md = Versioner(gever_doc).retrieve_version(0)
            new_version = Versioner(gever_doc).retrieve(1)
            new_version_md = Versioner(gever_doc).retrieve_version(1)

            self.assertEqual(initial_content, initial_version.file.data)
            self.assertEqual(initial_filename, initial_version.file.filename)
            self.assertEqual(u'Initial version', initial_version_md.comment)

            self.assertEqual(new_content, new_version.file.data)
            self.assertEqual(initial_filename, new_version.file.filename)
            self.assertEqual(u'Document copied back from teamraum', new_version_md.comment)

            self.assertEqual(
                RETRIEVAL_MODE_VERSION,
                browser.json.get('teamraum_connect_retrieval_mode'))

            self.assertEqual(u'', IDocumentMetadata(gever_doc).gever_url)

    @browsing
    def test_copy_eml_mail_from_a_workspace(self, browser):
        mail = create(Builder("mail")
                      .with_message(MAIL_DATA)
                      .within(self.workspace))
        transaction.commit()

        payload = {
            'workspace_uid': self.workspace.UID(),
            'document_uid': mail.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, mail)
            with self.observe_children(self.dossier) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            self.assertEqual(len(children['added']), 1)
            mail_copy = children['added'].pop()

            self.assertEqual(mail_copy.absolute_url(), browser.json.get('@id'))
            self.assertEqual(mail_copy.title, mail.title)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(mail_copy))

            self.assertEqual(
                RETRIEVAL_MODE_COPY,
                browser.json.get('teamraum_connect_retrieval_mode'))

    @browsing
    def test_copy_msg_mail_from_a_workspace(self, browser):
        msg = load('testmail.msg')
        command = CreateEmailCommand(
            self.workspace,
            'testm\xc3\xa4il.msg',
            msg)

        mail = command.execute()
        transaction.commit()

        payload = {
            'workspace_uid': self.workspace.UID(),
            'document_uid': mail.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, mail)
            with self.observe_children(self.dossier) as children:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

            self.assertEqual(len(children['added']), 1)
            mail_copy = children['added'].pop()

            self.assertEqual(mail_copy.absolute_url(), browser.json.get('@id'))
            self.assertEqual(mail_copy.title, mail.title)

            self.assertItemsEqual(
                manager._serialized_document_schema_fields(mail),
                manager._serialized_document_schema_fields(mail_copy))

            self.assertEqual(
                RETRIEVAL_MODE_COPY,
                browser.json.get('teamraum_connect_retrieval_mode'))

    @browsing
    def test_copying_document_from_workspace_is_prevented_if_checked_out(self, browser):
        document = create(Builder('document')
                          .within(self.workspace)
                          .with_dummy_content())

        manager = getMultiAdapter((document, self.request), ICheckinCheckoutManager)
        manager.checkout()

        payload = {
            'workspace_uid': self.workspace.UID(),
            'document_uid': document.UID(),
        }

        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

            browser.login()
            fix_publisher_test_bug(browser, document)
            with self.observe_children(self.dossier) as children:
                with browser.expect_http_error(code=400):
                    browser.open(
                        self.dossier.absolute_url() + '/@copy-document-from-workspace',
                        data=json.dumps(payload),
                        method='POST',
                        headers={'Accept': 'application/json',
                                 'Content-Type': 'application/json'},
                    )

            self.assertEqual(len(children['added']), 0)
            self.assertEqual(
                {u'type': u'BadRequest',
                 u'additional_metadata': {},
                 u'message': u"Document can't be copied from workspace "
                             u"because it's currently checked out",
                 u'translated_message': u"Document can't be copied from workspace "
                                        u"because it's currently checked out."},
                browser.json)


class TestAddParticipationsOnWorkspacePost(FunctionalWorkspaceClientTestCase):

    def setUp(self):
        super(TestAddParticipationsOnWorkspacePost, self).setUp()

        # Create a workspaces users
        self.workspaces_user = api.user.create(email="foo@example.com",
                                               username='workspaces.user')

        self.grant('WorkspacesUser', 'WorkspacesCreator',
                   on=self.workspace_root,
                   user_id=self.workspaces_user.getId())

        # Grant WorkspaceAdmin to TEST_USER
        self.grant('WorkspaceAdmin', on=self.workspace)

        # Link the workspace to the dossier
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

    @browsing
    def test_add_participations_raises_for_missing_workspace_uid(self, browser):

        payload = {
            'participants': [{"participant": self.workspaces_user.getId(),
                              "role": "WorkspaceGuest"}],
            }

        with self.workspace_client_env(), browser.expect_http_error(code=400):
            browser.login()
            browser.open(
                self.dossier.absolute_url() + '/@linked-workspace-participations',
                data=json.dumps(payload),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )

        self.assertNotIn(u'workspaces.user',
                         self.workspace.__ac_local_roles__)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'workspace_uid_required',
             u'translated_message': u"Property 'workspace_uid' is required",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_add_participations_raises_for_missing_participants(self, browser):

        payload = {
            'workspace_uid': self.workspace.UID(),
            }

        with self.workspace_client_env(), browser.expect_http_error(code=400):
            browser.login()
            browser.open(
                self.dossier.absolute_url() + '/@linked-workspace-participations',
                data=json.dumps(payload),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'participant_required',
             u'translated_message': u"Property 'participants' is required",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_add_participations_raises_if_user_is_not_workspace_admin(self, browser):
        self.grant('WorkspaceMember', on=self.workspace)

        payload = {
            'workspace_uid': self.workspace.UID(),
            'participants': [{"participant": self.workspaces_user.getId(),
                              "role": "WorkspaceGuest"}]
            }

        with self.workspace_client_env():
            browser.login()
            browser.exception_bubbling = True
            with self.assertRaises(HTTPServerError):
                browser.open(
                    self.dossier.absolute_url() + '/@linked-workspace-participations',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                    )

        self.assertEqual(
            {u'message': u'Error while communicating with the teamraum deployment',
             u'service_error': {
                u'message': u'You are not authorized to access this resource.',
                u'status_code': 401,
                u'type': u'Unauthorized'},
             u'type': u'Bad Gateway'},
            browser.json)

    @browsing
    def test_add_participations_raises_for_invalid_participant(self, browser):

        payload = {
            'workspace_uid': self.workspace.UID(),
            'participants': [{"participant": "invalid",
                              "role": "WorkspaceGuest"}]
            }

        with self.workspace_client_env():
            browser.login()
            browser.exception_bubbling = True
            with self.assertRaises(HTTPServerError):
                browser.open(
                    self.dossier.absolute_url() + '/@linked-workspace-participations',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual(502, browser.status_code)
        self.assertEqual(
            {u'message': u'Error while communicating with the teamraum deployment',
             u'service_error': {
                u'additional_metadata': {},
                u'message': u'disallowed_participant',
                u'status_code': 400,
                u'translated_message': u'The participant invalid is not allowed',
                u'type': u'BadRequest'},
             u'type': u'Bad Gateway'},
            browser.json)

    @browsing
    def test_add_participations_raises_for_invalid_role(self, browser):

        payload = {
            'workspace_uid': self.workspace.UID(),
            'participants': [{"participant": self.workspaces_user.getId(),
                              "role": "invalid"}]
            }

        with self.workspace_client_env():
            browser.login()
            browser.exception_bubbling = True
            with self.assertRaises(HTTPServerError):
                browser.open(
                    self.dossier.absolute_url() + '/@linked-workspace-participations',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual(502, browser.status_code)
        self.assertEqual(
            {u'message': u'Error while communicating with the teamraum deployment',
             u'service_error': {
                u'additional_metadata': {},
                u'message': u'invalid_role',
                u'status_code': 400,
                u'translated_message': u"Role invalid is not available. "
                                       u"Available roles are: ['WorkspaceAdmin', "
                                       u"'WorkspaceMember', 'WorkspaceGuest']",
                u'type': u'BadRequest'},
             u'type': u'Bad Gateway'},
            browser.json)

    @browsing
    def test_add_participations_handles_multiple_participants(self, browser):
        # Create second workspaces user
        workspaces_user2 = api.user.create(email="bar@example.com",
                                           username='workspaces.user2')

        self.grant('WorkspacesUser',
                   on=self.workspace_root,
                   user_id=workspaces_user2.getId())

        payload = {
            'workspace_uid': self.workspace.UID(),
            'participants': [{"participant": self.workspaces_user.getId(),
                              "role": "WorkspaceGuest"},
                             {"participant": workspaces_user2.getId(),
                              "role": "WorkspaceMember"}],
            }

        self.assertEqual(
            {'test_user_1_': ['WorkspaceAdmin']},
            self.workspace.__ac_local_roles__)

        with self.workspace_client_env():
            browser.login()
            browser.open(
                self.dossier.absolute_url() + '/@linked-workspace-participations',
                data=json.dumps(payload),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )

        items = browser.json.get("items")
        self.assertEqual(2, len(items))
        self.assertEqual("workspaces.user",
                         items[0]["participant"]["id"])
        self.assertEqual({u'token': u'WorkspaceGuest', u'title': u'Guest'},
                         items[0]["role"])
        self.assertEqual("workspaces.user2",
                         items[1]["participant"]["id"])
        self.assertEqual({u'token': u'WorkspaceMember', u'title': u'Member'},
                         items[1]["role"])

        self.assertEqual(
            {u'workspaces.user': [u'WorkspaceGuest'],
             u'workspaces.user2': [u'WorkspaceMember'],
             'test_user_1_': ['WorkspaceAdmin']},
            self.workspace.__ac_local_roles__)


class TestAddInvitationOnWorkspacePost(FunctionalWorkspaceClientTestCase):

    def setUp(self):
        super(TestAddInvitationOnWorkspacePost, self).setUp()

        self.participation_manager = ManageParticipants(self.workspace, self.request)

        # Grant WorkspaceAdmin to TEST_USER
        self.grant('WorkspaceAdmin', on=self.workspace)

        # Link the workspace to the dossier
        with self.workspace_client_env():
            manager = ILinkedWorkspaces(self.dossier)
            manager.storage.add(self.workspace.UID())
            transaction.commit()

    @browsing
    def test_add_invitation_raises_for_missing_workspace_uid(self, browser):

        payload = {
            'recipient_email': 'max.muster@example.com',
            'role': {'token': WORKSPCAE_GUEST.id},
        }

        self.assertEqual([], self.participation_manager.get_pending_invitations())

        with self.workspace_client_env(), browser.expect_http_error(code=400):
            browser.login()
            browser.open(
                self.dossier.absolute_url() + '/@linked-workspace-invitations',
                data=json.dumps(payload),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )

        self.assertEqual([], self.participation_manager.get_pending_invitations())
        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'workspace_uid_required',
             u'translated_message': u"Property 'workspace_uid' is required",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_add_invitation_raises_for_missing_recipient_email(self, browser):

        payload = {
            'workspace_uid': self.workspace.UID(),
            'role': {'token': WORKSPCAE_GUEST.id},
        }

        self.assertEqual([], self.participation_manager.get_pending_invitations())

        with self.workspace_client_env(), browser.expect_http_error(code=400):
            browser.login()
            browser.open(
                self.dossier.absolute_url() + '/@linked-workspace-invitations',
                data=json.dumps(payload),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )

        self.assertEqual([], self.participation_manager.get_pending_invitations())
        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'recipient_email_required',
             u'translated_message': u"Property 'recipient_email' is required",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_add_invitation_raises_for_missing_role(self, browser):

        payload = {
            'workspace_uid': self.workspace.UID(),
            'recipient_email': 'max.muster@example.com',
        }

        self.assertEqual([], self.participation_manager.get_pending_invitations())

        with self.workspace_client_env(), browser.expect_http_error(code=400):
            browser.login()
            browser.open(
                self.dossier.absolute_url() + '/@linked-workspace-invitations',
                data=json.dumps(payload),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )

        self.assertEqual([], self.participation_manager.get_pending_invitations())
        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'role_required',
             u'translated_message': u"Property 'role' is required",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_add_invitation_raises_if_user_is_not_workspace_admin(self, browser):
        self.grant('WorkspaceMember', on=self.workspace)

        payload = {
            'workspace_uid': self.workspace.UID(),
            'recipient_email': 'max.muster@example.com',
            'role': {'token': WORKSPCAE_GUEST.id},
        }

        self.assertEqual([], self.participation_manager.get_pending_invitations())

        with self.workspace_client_env():
            browser.login()
            browser.exception_bubbling = True
            with self.assertRaises(HTTPServerError):
                browser.open(
                    self.dossier.absolute_url() + '/@linked-workspace-invitations',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual([], self.participation_manager.get_pending_invitations())
        self.assertEqual(
            {u'message': u'Error while communicating with the teamraum deployment',
             u'service_error': {
                 u'message': u'You are not authorized to access this resource.',
                 u'status_code': 401,
                 u'type': u'Unauthorized'},
             u'type': u'Bad Gateway'},
            browser.json)

    @browsing
    def test_add_invitation_adds_an_inivitation(self, browser):
        payload = {
            'workspace_uid': self.workspace.UID(),
            'recipient_email': 'max.muster@example.com',
            'role': {'token': WORKSPCAE_GUEST.id},
        }

        self.assertEqual([], self.participation_manager.get_pending_invitations())

        with self.workspace_client_env():
            browser.login()
            browser.open(
                self.dossier.absolute_url() + '/@linked-workspace-invitations',
                data=json.dumps(payload),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'},
            )

        self.assertEqual(1, len(self.participation_manager.get_pending_invitations()))
