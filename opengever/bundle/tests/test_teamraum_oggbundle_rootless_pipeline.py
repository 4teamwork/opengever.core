from Acquisition import aq_parent
from collective.transmogrifier.transmogrifier import Transmogrifier
from datetime import datetime
from opengever.bundle.console import add_guid_index
from opengever.bundle.loader import GUID_INDEX_NAME
from opengever.bundle.sections.bundlesource import BUNDLE_INGESTION_SETTINGS_KEY  # noqa
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix  # noqa
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_filename
from plone import api
from Products.CMFPlone.utils import safe_hasattr
from zope.annotation import IAnnotations
import pytz


FROZEN_NOW = datetime(2016, 12, 20, 9, 40)


class TestTeamraumOggBundleRootlessPipeline(IntegrationTestCase):

    def remove_existing_workspace_content(self):
        # Remove all todos first, because otherwise they prevent deletion
        # of the containing todo lists, and therefore workspaces
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(portal_type='opengever.workspace.todo')
        todos = [b.getObject() for b in brains]
        for todo in todos:
            aq_parent(todo).manage_delObjects([todo.id])

        workspace_root = self.portal['workspaces']
        workspace_root.manage_delObjects(['workspace-1'])
        # Reset sequence number counters
        seq_counters = IAnnotations(self.portal)['ISequenceNumber.sequence_number']
        del seq_counters['WorkspaceSequenceNumberGenerator']
        del seq_counters['WorkspaceFolderSequenceNumberGenerator']

    def test_oggbundle_transmogrifier(self):
        # this is a bit hackish, but since builders currently don't work in
        # layer setup/teardown and isolation of database content is ensured
        # on a per test level we abuse just one test to setup the pipeline and
        # test its data.

        self.login(self.manager)

        self.remove_existing_workspace_content()

        # Create the 'bundle_guid' index. In production, this will be done
        # by the "bin/instance import" command in opengever.bundle.console
        add_guid_index()

        # load pipeline
        transmogrifier = Transmogrifier(api.portal.get())
        annotations = IAnnotations(transmogrifier)
        annotations[BUNDLE_PATH_KEY] = resource_filename(
            'opengever.bundle.tests', 'assets/teamraum_rootless.oggbundle')

        transmogrifier(u'opengever.bundle.oggbundle')
        bundle = annotations[BUNDLE_KEY]

        workspaceroot = self.portal['workspaces']
        workspace = self.assert_workspace_created(workspaceroot)
        workspacefolder = self.assert_workspacefolder_created(workspace)

        self.assert_report_data_collected(bundle)

    def assert_workspace_created(self, workspaceroot):
        workspace = workspaceroot.get('workspace-1')

        self.assertEqual(u'Rootless Teamraum B\xe4rengraben', workspace.title)
        self.assertEqual(u'Lorem Ipsum B\xe4rengraben', workspace.description)
        self.assertEqual(
            datetime(2020, 8, 3, 11, 45, 30, 123456, tzinfo=pytz.UTC),
            workspace.changed)

        self.assertEqual(
            'opengever_workspace--STATUS--active',
            api.content.get_state(workspace))

        self.assertDictContainsSubset(
            {'admin_users': ['WorkspaceAdmin']},
            workspace.__ac_local_roles__)
        self.assertDictContainsSubset(
            {'privileged_users': ['WorkspaceMember']},
            workspace.__ac_local_roles__)
        self.assertDictContainsSubset(
            {'all_users': ['WorkspaceGuest']},
            workspace.__ac_local_roles__)
        self.assertFalse(safe_hasattr(workspace, '__ac_local_roles_block__'))

        self.assertEqual(
            IAnnotations(workspace)[BUNDLE_GUID_KEY],
            index_data_for(workspace)[GUID_INDEX_NAME])
        return workspace

    def assert_workspacefolder_created(self, workspace):
        workspacefolder = workspace.get('folder-1')

        self.assertEqual(u'Rootless Teamraum Folder B\xe4rengraben', workspacefolder.title)
        self.assertEqual(u'Lorem Ipsum Folder B\xe4rengraben', workspacefolder.description)
        self.assertEqual(
            datetime(2020, 8, 3, 12, 35, 30, 123456, tzinfo=pytz.UTC),
            workspacefolder.changed)

        self.assertEqual(
            'opengever_workspace_folder--STATUS--active',
            api.content.get_state(workspacefolder))

        self.assertDictContainsSubset(
            {'admin_users': ['WorkspaceAdmin']},
            workspacefolder.__ac_local_roles__)
        self.assertDictContainsSubset(
            {'privileged_users': ['WorkspaceMember']},
            workspacefolder.__ac_local_roles__)
        self.assertDictContainsSubset(
            {'all_users': ['WorkspaceGuest']},
            workspacefolder.__ac_local_roles__)
        self.assertFalse(safe_hasattr(workspacefolder, '__ac_local_roles_block__'))

        self.assertEqual(
            IAnnotations(workspacefolder)[BUNDLE_GUID_KEY],
            index_data_for(workspacefolder)[GUID_INDEX_NAME])
        return workspacefolder

    def assert_report_data_collected(self, bundle):
        report_data = bundle.report_data
        metadata = report_data['metadata']

        self.assertSetEqual(
            set([
                'opengever.repository.repositoryroot',
                'opengever.repository.repositoryfolder',
                'opengever.inbox.container',
                'opengever.inbox.inbox',
                'opengever.private.root',
                'opengever.dossier.templatefolder',
                'opengever.workspace.root',
                'opengever.workspace.workspace',
                'opengever.workspace.folder',
                'opengever.dossier.businesscasedossier',
                'opengever.document.document',
                'ftw.mail.mail',
                '_opengever.ogds.models.user.User']),
            set(metadata.keys()))

        workspaceroots = metadata['opengever.workspace.root']
        workspaces = metadata['opengever.workspace.workspace']
        workspacefolders = metadata['opengever.workspace.folder']
        reporoots = metadata['opengever.repository.repositoryroot']
        repofolders = metadata['opengever.repository.repositoryfolder']
        inboxcontainers = metadata['opengever.inbox.container']
        inboxes = metadata['opengever.inbox.inbox']
        privateroots = metadata['opengever.private.root']
        templatefolders = metadata['opengever.dossier.templatefolder']
        dossiers = metadata['opengever.dossier.businesscasedossier']
        documents = metadata['opengever.document.document']
        mails = metadata['ftw.mail.mail']
        ogds_users = metadata['_opengever.ogds.models.user.User']

        self.assertEqual(0, len(workspaceroots))
        self.assertEqual(1, len(workspaces))
        self.assertEqual(1, len(workspacefolders))
        self.assertEqual(0, len(reporoots))
        self.assertEqual(0, len(repofolders))
        self.assertEqual(0, len(inboxcontainers))
        self.assertEqual(0, len(inboxes))
        self.assertEqual(0, len(privateroots))
        self.assertEqual(0, len(templatefolders))
        self.assertEqual(0, len(dossiers))
        self.assertEqual(0, len(documents))
        self.assertEqual(0, len(mails))
        self.assertEqual(0, len(ogds_users))
