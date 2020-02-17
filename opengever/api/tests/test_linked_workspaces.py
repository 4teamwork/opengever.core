from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import HTTPServerError
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.storage import LinkedWorkspacesStorage
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from zExceptions import BadRequest
from zExceptions import NotFound
from zExceptions import Unauthorized
import json
import requests_mock
import transaction


def fix_publisher_test_bug(browser, obj):
    # We need to make a GET request before using the `@create-linked-workspace`
    # endpoint. This is a workaround to fix a weird issue where we get
    # a silent `ConflictError`. ZPublisher will then automatically
    # republish the request although the previous POST request has
    # already been handled successfully, effectively creating the new
    # workspace twice
    #
    # If we get the dossier first, before creating a workspace, it seems
    # to work properly.
    #
    # This issue only appears in a testing environment.
    browser.open(obj, method='GET', headers={'Accept': 'application/json'})


class TestLinkedWorkspacesPost(FunctionalWorkspaceClientTestCase):

    @browsing
    def test_create_linked_workspace(self, browser):
        browser.login()
        with self.observe_children(self.workspace_root) as children:
            with self.workspace_client_env():
                fix_publisher_test_bug(browser, self.dossier)
                browser.open(
                    self.dossier.absolute_url() + '/@create-linked-workspace',
                    data=json.dumps({"title": "My linked workspace"}),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual(200, browser.status_code)
        self.assertEqual(1, len(children['added']))
        linked_workspace = children['added'].pop()

        self.assertIn(browser.json.get('@id'),
                      linked_workspace.absolute_url())
        self.assertIn(browser.json.get('title'),
                      linked_workspace.title)

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

    @browsing
    def test_get_linked_workspaces_replaces_service_url_with_actual_request_url(self, browser):
        url = self.dossier.absolute_url() + '/@linked-workspaces'
        with self.workspace_client_env():
            browser.login()
            response = browser.open(url, method='GET', headers={'Accept': 'application/json'}).json

            self.assertEqual(url, response.get('@id'))

    @browsing
    def test_raise_exception_for_subdossiers(self, browser):
        subdossier = create(Builder('dossier').within(self.dossier))
        transaction.commit()
        browser.login()

        with self.workspace_client_env():
            browser.exception_bubbling = True
            with self.assertRaises(BadRequest):
                browser.open(
                    subdossier.absolute_url() + '/@linked-workspaces',
                    method='GET', headers={'Accept': 'application/json'}).json

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

        self.assertEqual("Property 'workspace_uid' is required", str(cm.exception))

    @browsing
    def test_raises_when_document_uid_missing(self, browser):
        payload = {
            'workspace_uid': self.workspace.UID()
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
            'workspace_uid': self.workspace.UID()
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
            'workspace_uid': self.workspace.UID()
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
            'workspace_uid': self.workspace.UID()
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

            workspace_document = children['added'].pop()
            self.assertEqual(workspace_document.absolute_url(), browser.json.get('@id'))
