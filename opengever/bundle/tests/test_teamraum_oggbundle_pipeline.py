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


FROZEN_NOW = datetime(2016, 12, 20, 9, 40)


class TestTeamraumOggBundlePipeline(IntegrationTestCase):

    def remove_existing_workspace_content(self):
        # Remove all todosfirst, because otherwise they prevent deletion
        # of the containing todo lists, and therefore workspaces
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(portal_type='opengever.workspace.todo')
        todos = [b.getObject() for b in brains]
        for todo in todos:
            aq_parent(todo).manage_delObjects([todo.id])

        self.portal.manage_delObjects(['workspaces'])

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
            'opengever.bundle.tests', 'assets/teamraum.oggbundle')

        transmogrifier(u'opengever.bundle.oggbundle')
        bundle = annotations[BUNDLE_KEY]

        self.assert_workspaceroot_created()

        self.assert_report_data_collected(bundle)

    def assert_workspaceroot_created(self):
        root = self.portal.get('opengever-workspace.root')

        self.assertEqual(u'Teamr\xe4ume', root.title_de)
        self.assertEqual(u'Espace partag\xe9', root.title_fr)

        self.assertEqual(
            'opengever_workspace_root--STATUS--active',
            api.content.get_state(root))

        self.assertDictContainsSubset(
            {'admin_users': ['WorkspacesCreator']},
            root.__ac_local_roles__)
        self.assertDictContainsSubset(
            {'all_users': ['WorkspacesUser']},
            root.__ac_local_roles__)
        self.assertFalse(safe_hasattr(root, '__ac_local_roles_block__'))

        self.assertEqual(
            IAnnotations(root)[BUNDLE_GUID_KEY],
            index_data_for(root)[GUID_INDEX_NAME])
        return root

    def assert_report_data_collected(self, bundle):
        report_data = bundle.report_data
        metadata = report_data['metadata']

        self.assertSetEqual(
            set([
                'opengever.repository.repositoryroot',
                'opengever.repository.repositoryfolder',
                'opengever.workspace.root',
                'opengever.dossier.businesscasedossier',
                'opengever.document.document',
                'ftw.mail.mail']),
            set(metadata.keys()))

        workspaceroots = metadata['opengever.workspace.root']
        reporoots = metadata['opengever.repository.repositoryroot']
        repofolders = metadata['opengever.repository.repositoryfolder']
        dossiers = metadata['opengever.dossier.businesscasedossier']
        documents = metadata['opengever.document.document']
        mails = metadata['ftw.mail.mail']

        self.assertEqual(1, len(workspaceroots))
        self.assertEqual(0, len(reporoots))
        self.assertEqual(0, len(repofolders))
        self.assertEqual(0, len(dossiers))
        self.assertEqual(0, len(documents))
        self.assertEqual(0, len(mails))
