from Acquisition import aq_parent
from collective.transmogrifier.transmogrifier import Transmogrifier
from datetime import date
from datetime import datetime
from DateTime import DateTime
from ftw.testing import freeze
from opengever.base.behaviors.classification import IClassification
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
import tzlocal


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
        # Reset sequence number counters
        seq_counters = IAnnotations(self.portal)['ISequenceNumber.sequence_number']
        del seq_counters['WorkspaceSequenceNumberGenerator']
        del seq_counters['WorkspaceFolderSequenceNumberGenerator']

    def find_by_title(self, parent, title):
        matching_children = [child for child in parent.objectValues()
                             if getattr(child, "title", None) == title]
        for child in parent.objectValues():
            object_title = getattr(child, "title", None)
            if object_title == title:
                return child

        self.assertTrue(
            matching_children,
            msg="did not find object with title: {}".format(title))
        self.assertEqual(
            1, len(matching_children),
            msg="found more than one object with title: {}".format(title))
        return matching_children[0]

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

        with freeze(FROZEN_NOW):
            transmogrifier(u'opengever.bundle.oggbundle')
        bundle = annotations[BUNDLE_KEY]

        workspaceroot = self.assert_workspaceroot_created()
        workspace = self.assert_workspace_created(workspaceroot)
        workspacefolder = self.assert_workspacefolder_created(workspace)
        self.assert_document_created(workspacefolder)
        self.assert_mail_created(workspace)

        self.assert_report_data_collected(bundle)

    def assert_workspaceroot_created(self):
        root = self.portal.get('workspaces')

        self.assertEqual(u'Teamr\xe4ume', root.title_de)
        self.assertEqual(u'Espace partag\xe9', root.title_fr)
        self.assertEqual(u'Workspaces', root.title_en)

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

        placeful_workflow = api.portal.get_tool('portal_placeful_workflow')
        config = placeful_workflow.getWorkflowPolicyConfig(root)
        self.assertEqual(
            "opengever_workspace_policy", config.getPolicyInId())
        self.assertEqual(
            "opengever_workspace_policy", config.getPolicyBelowId())

        return root

    def assert_workspace_created(self, workspaceroot):
        workspace = workspaceroot.get('workspace-1')

        self.assertEqual(u'Teamraum B\xe4rengraben', workspace.title)
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

        self.assertEqual(u'Teamraum Folder B\xe4rengraben', workspacefolder.title)
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

    def assert_document_created(self, parent):
        document1 = self.find_by_title(parent, u'Bewerbung Hanspeter M\xfcller')

        self.assertTrue(document1.digitally_available)
        self.assertIsNotNone(document1.file)
        self.assertEqual(22198, len(document1.file.data))

        self.assertEqual(
            u'david.erni',
            document1.document_author)
        self.assertEqual(
            date(2007, 1, 1),
            document1.document_date)
        self.assertEqual(
            document1.modified(),
            DateTime("2019-12-05T14:09:59.240726"))
        self.assertEqual(
            document1.changed,
            tzlocal.get_localzone().localize(datetime(2019, 12, 5, 14, 9, 59, 240726)))

        self.assertEqual(
            tuple(),
            document1.keywords)
        self.assertTrue(
            document1.preserved_as_paper)
        self.assertEqual(
            [],
            document1.relatedItems)
        self.assertEqual(
            'opengever_workspace_document--STATUS--active',
            api.content.get_state(document1))
        self.assertEqual(
            IAnnotations(document1)[BUNDLE_GUID_KEY],
            index_data_for(document1)[GUID_INDEX_NAME])

    def assert_mail_created(self, parent):
        mail = self.find_by_title(parent, u'Ein Mail')

        self.assertTrue(mail.digitally_available)
        self.assertIsNotNone(mail.message)
        self.assertEqual(920, len(mail.message.data))

        self.assertEqual(
            u'Peter Muster <from@example.org>',
            mail.document_author)

        # Setting the document date in the bundle for an e-mail has no effect
        # The date from the E-mail is used instead
        self.assertNotEqual(
            date(2011, 1, 1),
            mail.document_date)
        self.assertEqual(
            date(2013, 1, 1),
            mail.document_date)

        self.assertEqual(
            mail.modified(),
            DateTime("2019-12-05"))
        self.assertEqual(
            mail.changed,
            tzlocal.get_localzone().localize(datetime(2019, 12, 5)))

        self.assertEqual(
            None,
            mail.document_type)
        self.assertEqual(
            tuple(),
            mail.keywords)
        self.assertTrue(
            mail.preserved_as_paper)
        self.assertEqual(
            u'unchecked',
            IClassification(mail).public_trial)
        self.assertEqual(
            u'',
            IClassification(mail).public_trial_statement)
        self.assertEqual(
            FROZEN_NOW.date(),
            mail.receipt_date)
        self.assertEqual(
            'mail-state-active',
            api.content.get_state(mail))

        self.assertEqual(
            IAnnotations(mail)[BUNDLE_GUID_KEY],
            index_data_for(mail)[GUID_INDEX_NAME])

    def assert_report_data_collected(self, bundle):
        report_data = bundle.report_data
        metadata = report_data['metadata']

        self.assertSetEqual(
            set([
                'opengever.repository.repositoryroot',
                'opengever.repository.repositoryfolder',
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
        privateroots = metadata['opengever.private.root']
        templatefolders = metadata['opengever.dossier.templatefolder']
        dossiers = metadata['opengever.dossier.businesscasedossier']
        documents = metadata['opengever.document.document']
        mails = metadata['ftw.mail.mail']
        ogds_users = metadata['_opengever.ogds.models.user.User']

        self.assertEqual(1, len(workspaceroots))
        self.assertEqual(1, len(workspaces))
        self.assertEqual(1, len(workspacefolders))
        self.assertEqual(0, len(reporoots))
        self.assertEqual(0, len(repofolders))
        self.assertEqual(0, len(privateroots))
        self.assertEqual(0, len(templatefolders))
        self.assertEqual(0, len(dossiers))
        self.assertEqual(1, len(documents))
        self.assertEqual(1, len(mails))
        self.assertEqual(0, len(ogds_users))
