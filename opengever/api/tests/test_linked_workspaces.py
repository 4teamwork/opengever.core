from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import HTTPServerError
from opengever.base.behaviors.classification import IClassification
from opengever.base.command import CreateEmailCommand
from opengever.base.oguid import Oguid
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.locking.lock import LOCK_TYPE_COPIED_TO_WORKSPACE_LOCK
from opengever.mail.tests import MAIL_DATA
from opengever.testing.assets import load
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
        self.assertEqual(1, len(children['added']))
        linked_workspace = children['added'].pop()

        self.assertIn(browser.json.get('@id'),
                      linked_workspace.absolute_url())
        self.assertIn(browser.json.get('title'),
                      linked_workspace.title)
        self.assertIn(browser.json.get('external_reference'),
                      Oguid.for_object(self.dossier).id)

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
        self.assertEqual(Oguid.for_object(self.dossier).id, self.workspace.external_reference)

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
        self.assertEqual("Property 'workspace_uid' is required", str(cm.exception))

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

        self.assertEqual("Property 'workspace_uid' is required", str(cm.exception))

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
            browser.exception_bubbling = True
            with self.assertRaises(LookupError) as cm:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual(
            "Document not in linked workspace",
            str(cm.exception))

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
            browser.exception_bubbling = True
            with self.assertRaises(LookupError) as cm:
                browser.open(
                    self.dossier.absolute_url() + '/@copy-document-from-workspace',
                    data=json.dumps(payload),
                    method='POST',
                    headers={'Accept': 'application/json',
                             'Content-Type': 'application/json'},
                )

        self.assertEqual("Document not in linked workspace", str(cm.exception))

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
                               .attach_file_containing(new_content,
                                                       name=new_filename))

        ILinkedDocuments(workspace_doc).link_gever_document(IUUID(gever_doc))
        ILinkedDocuments(gever_doc).link_workspace_document(IUUID(workspace_doc))

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
                 u'message': u"Document can't be copied from workspace "
                             u"because it's currently checked out"},
                browser.json)

    @browsing
    def test_copying_document_from_workspace_into_a_classified_dossier_will_update_the_document_classification_if_it_does_not_meet_min_requirements(self, browser):
        document = create(Builder('document')
                          .within(self.workspace)
                          .with_dummy_content())

        payload = {
            'workspace_uid': self.workspace.UID(),
            'document_uid': document.UID(),
        }

        IClassification(self.dossier).classification = 'confidential'

        self.assertEqual('unprotected', document.classification)
        self.assertEqual('confidential', self.dossier.classification)

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

        self.assertEqual('confidential', document_copy.classification)

    @browsing
    def test_copying_a_higher_classified_document_from_workspace_into_a_classified_dossier_will_not_update_the_document_classification(self, browser):
        document = create(Builder('document')
                          .within(self.workspace)
                          .with_dummy_content())

        payload = {
            'workspace_uid': self.workspace.UID(),
            'document_uid': document.UID(),
        }

        IClassification(document).classification = 'classified'
        IClassification(self.dossier).classification = 'confidential'

        self.assertEqual('classified', document.classification)
        self.assertEqual('confidential', self.dossier.classification)

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

        self.assertEqual('classified', document_copy.classification)
