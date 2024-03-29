from opengever.base.oguid import Oguid
from opengever.testing import assets
from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.exceptions import WorkspaceClientFeatureNotEnabled
from opengever.workspaceclient.exceptions import WorkspaceURLMissing
from opengever.workspaceclient.interfaces import ILinkedDocuments
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from zExceptions import Unauthorized
import transaction


class TestWorkspaceClient(FunctionalWorkspaceClientTestCase):

    def test_raises_an_error_if_using_the_client_with_disabled_feature(self):
        client = WorkspaceClient()
        self.enable_feature(False)
        with self.assertRaises(WorkspaceClientFeatureNotEnabled):
            client.get('/')

    def test_raises_an_error_if_the_workspace_url_is_not_configured(self):
        client = WorkspaceClient()
        with self.env(TEAMRAUM_URL=''):
            with self.assertRaises(WorkspaceURLMissing):
                client.get('/')

    def test_raises_an_error_if_user_lacks_neccesary_permissions(self):
        with self.workspace_client_env() as client:
            client.request.get('/').json()

            roles = set(api.user.get_roles())
            self.grant(roles.difference({'WorkspaceClientUser'}))
            with self.assertRaises(Unauthorized):
                client.request.get('/').json()

    def test_make_requests_to_the_configured_workspace(self):
        with self.workspace_client_env() as client:
            response = client.request.get('/').json()

        self.assertEqual(self.portal.absolute_url(), response.get('@id'))

    def test_get_an_object(self):
        with self.workspace_client_env() as client:
            response = client.get(self.workspace.absolute_url())

        self.assertEqual(self.workspace.absolute_url(), response.get('@id'))

    def test_search_for_objects(self):
        with self.workspace_client_env() as client:
            response = client.search(UID=[self.workspace.UID()])

        self.assertEqual(1, response.get('items_total'))
        self.assertEqual(self.workspace.absolute_url(),
                         response.get('items')[0].get('@id'))

    def test_create_workspace(self):
        with self.observe_children(self.workspace_root) as children:
            with self.workspace_client_env() as client:
                response = client.create_workspace(title=u"My new w\xf6rkspace")
                transaction.commit()

        self.assertEqual(u"My new w\xf6rkspace", response.get('title'))

        workspace = children['added'].pop()
        self.assertEqual(workspace.title, response.get('title'))

    def test_link_to_workspace(self):
        dossier_oguid = Oguid.for_object(self.dossier).id
        with self.workspace_client_env() as client:
            response = client.link_to_workspace(self.workspace.UID(), dossier_oguid)
            transaction.commit()

        self.assertEqual(self.workspace.title, response.get('title'))
        self.assertEqual(dossier_oguid, response.get('external_reference'))
        self.assertEqual(dossier_oguid, self.workspace.external_reference)

    def test_link_to_workspace_raises_if_workspace_is_already_linked(self):
        dossier_oguid = Oguid.for_object(self.dossier).id
        self.workspace.external_reference = "fd:123"
        with self.workspace_client_env() as client:
            with self.assertRaises(LookupError) as error:
                client.link_to_workspace(self.workspace.UID(), dossier_oguid)
            self.assertEqual("Workspace is already linked to a dossier", str(error.exception))

    def test_lookup_url_by_uid_raises_if_nothing_found(self):
        with self.workspace_client_env() as client:
            with self.assertRaises(LookupError) as error:
                client.lookup_url_by_uid('not-existing-uid')
            self.assertEqual("Did not find object with UID not-existing-uid", str(error.exception))

    def test_lookup_url_by_uid_returns_the_absolute_url_to_the_obeject_if_found(self):
        with self.workspace_client_env() as client:
            url = client.lookup_url_by_uid(self.workspace.UID())
            self.assertEqual(self.workspace.absolute_url(), url)

    def test_upload_document_copy(self):
        with self.workspace_client_env() as client:
            filepath = assets.path_to_asset('vertragsentwurf.docx')
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            document_metadata = {
                '@type': 'opengever.document.document',
                'title': u"My new d\xf6kument",
                'description': u'Fantastic'
            }

            with self.observe_children(self.workspace) as children:
                response = client.upload_document_copy(
                    self.workspace.absolute_url(),
                    open(filepath, 'r'), content_type,
                    'vertragsentwurf.docx', document_metadata, 'UID-1234')
                transaction.commit()

            self.assertEqual(1, len(children['added']))
            document = children['added'].pop()

            self.assertEqual(document.absolute_url(), response.get('@id'))
            self.assertEqual(open(filepath, 'r').read(),
                             document.file.open().read())

            self.assertEqual(u'My new doekument.docx', document.file.filename)
            self.assertEqual(u'My new d\xf6kument', document.title)
            self.assertEqual('Fantastic', document.description)

            self.assertEqual(
                {'UID': 'UID-1234'},
                ILinkedDocuments(document).linked_gever_document)

    def test_unlink_workspace(self):
        dossier_oguid = Oguid.for_object(self.dossier).id
        with self.workspace_client_env() as client:
            client.link_to_workspace(self.workspace.UID(), dossier_oguid)
            transaction.commit()
            self.assertEqual(dossier_oguid, self.workspace.external_reference)
            gever_url = '{}/@resolve-oguid?oguid={}'.format(
                api.portal.get().absolute_url(), dossier_oguid)
            self.assertEqual(gever_url, self.workspace.gever_url)

            client.unlink_workspace(self.workspace.UID())
            transaction.commit()
            self.assertEqual(u'', self.workspace.external_reference)
            self.assertEqual(u'', self.workspace.gever_url)

    def test_unlink_deactivated_workspace(self):
        dossier_oguid = Oguid.for_object(self.dossier).id
        with self.workspace_client_env() as client:
            client.link_to_workspace(self.workspace.UID(), dossier_oguid)
            transaction.commit()
            self.assertEqual(dossier_oguid, self.workspace.external_reference)
            gever_url = '{}/@resolve-oguid?oguid={}'.format(
                api.portal.get().absolute_url(), dossier_oguid)
            self.assertEqual(gever_url, self.workspace.gever_url)

            self.grant('WorkspaceAdmin', *api.user.get_roles(), on=self.workspace)
            api.content.transition(
                self.workspace,
                'opengever_workspace--TRANSITION--deactivate--active_inactive')
            transaction.commit()

            client.unlink_workspace(self.workspace.UID())
            transaction.commit()
            self.assertEqual(u'', self.workspace.external_reference)
            self.assertEqual(u'', self.workspace.gever_url)
