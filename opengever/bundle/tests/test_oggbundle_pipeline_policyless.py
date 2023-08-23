from collective.transmogrifier.transmogrifier import Transmogrifier
from datetime import datetime
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.bundle.console import add_guid_index
from opengever.bundle.sections.bundlesource import BUNDLE_INGESTION_SETTINGS_KEY  # noqa
from opengever.bundle.sections.bundlesource import BUNDLE_INJECT_INITIAL_CONTENT_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.ogds.models.service import ogds_service
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix  # noqa
from opengever.repository.behaviors.responsibleorg import IResponsibleOrgUnit
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_filename
from plone import api
from zope.annotation import IAnnotations


FROZEN_NOW = datetime(2016, 12, 20, 9, 40)


class InitContentTestBase(object):

    def clear_initial_content(self):
        """Delete initial content created by fixture.
        """
        self.login(self.manager)
        self.portal.manage_delObjects(['eingangskorb'])
        self.portal.manage_delObjects(['private'])
        self.portal.manage_delObjects(['vorlagen'])

        catalog = api.portal.get_tool('portal_catalog')
        initial_content = catalog(portal_type=[
            'opengever.inbox.container',
            'opengever.inbox.inbox',
            'opengever.private.root',
            'opengever.dossier.templatefolder',
        ])
        assert len(initial_content) == 0

    def remove_all_org_units_except_one(self):
        org_units = ogds_service().all_org_units()
        create_session().delete(org_units[-1])
        assert len(ogds_service().all_org_units()) == 1

    def setup_pipeline(self):
        self.login(self.manager)
        add_guid_index()

        transmogrifier = Transmogrifier(api.portal.get())
        annotations = IAnnotations(transmogrifier)
        annotations[BUNDLE_PATH_KEY] = resource_filename(
            'opengever.bundle.tests', 'assets/policyless_gever.oggbundle')

        # This is the key to this test case. It tells the bundle loader (via
        # the bundle source) to inject items for initial content into the
        # pipeline, if the respective types are not present in the bundle.
        annotations[BUNDLE_INJECT_INITIAL_CONTENT_KEY] = True
        return transmogrifier


class TestInitialContentForPolicylessBundle(IntegrationTestCase, InitContentTestBase):

    def setUp(self):
        super(TestInitialContentForPolicylessBundle, self).setUp()
        self.clear_initial_content()

    def test_policyless_bundle_initial_content(self):
        transmogrifier = self.setup_pipeline()

        with freeze(FROZEN_NOW):
            transmogrifier(u'opengever.bundle.oggbundle')

        inbox_container = self.assert_inbox_container_created()
        self.assert_inbox_fa_created(inbox_container)
        self.assert_inbox_rk_created(inbox_container)
        self.assert_private_root_created()
        self.assert_template_folder_created()

    def assert_inbox_container_created(self):
        inbox_container = self.portal.get('eingangskorb')
        self.assertEqual(u'opengever.inbox.container', inbox_container.portal_type)

        self.assertEqual(u'Eingangskorb', inbox_container.title_de)
        self.assertEqual({
            'admin': ['Owner'],
            'fa_inbox_users': ['Reader'],
            'rk_inbox_users': ['Reader']},
            inbox_container.__ac_local_roles__)
        self.assertFalse(getattr(inbox_container, '__ac_local_roles_block__', False))
        return inbox_container

    def assert_inbox_fa_created(self, inbox_container):
        inbox_fa = inbox_container.get('fa')
        self.assertEqual(u'opengever.inbox.inbox', inbox_fa.portal_type)

        self.assertEqual(u'Eingangskorb Finanz\xe4mt', inbox_fa.title_de)
        self.assertEqual(u'fa', IResponsibleOrgUnit(inbox_fa).responsible_org_unit)
        self.assertEqual({
            'admin': ['Owner'],
            'fa_inbox_users': ['Contributor', 'Editor', 'Reader']},
            inbox_fa.__ac_local_roles__)
        self.assertTrue(inbox_fa.__ac_local_roles_block__)

    def assert_inbox_rk_created(self, inbox_container):
        inbox_rk = inbox_container.get('rk')
        self.assertEqual(u'opengever.inbox.inbox', inbox_rk.portal_type)

        self.assertEqual(u'Eingangskorb Ratskanzl\xc3\xa4i', inbox_rk.title_de)
        self.assertEqual(u'rk', IResponsibleOrgUnit(inbox_rk).responsible_org_unit)
        self.assertEqual({
            'admin': ['Owner'],
            'rk_inbox_users': ['Contributor', 'Editor', 'Reader']},
            inbox_rk.__ac_local_roles__)
        self.assertTrue(inbox_rk.__ac_local_roles_block__)

    def assert_private_root_created(self):
        private_root = self.portal.get('private')
        self.assertEqual(u'Meine Ablage', private_root.title_de)
        self.assertEqual({
            'admin': ['Owner']},
            private_root.__ac_local_roles__)
        self.assertFalse(getattr(private_root, '__ac_local_roles_block__', False))

    def assert_template_folder_created(self):
        template_folder = self.portal.get('vorlagen')
        self.assertEqual(u'Vorlagen', template_folder.title_de)
        self.assertEqual({
            'admin': ['Owner'],
            'fa_inbox_users': ['Contributor', 'Editor'],
            'rk_inbox_users': ['Contributor', 'Editor'],
            'fa_users': ['Reader'],
            'rk_users': ['Reader']},
            template_folder.__ac_local_roles__)
        self.assertFalse(getattr(template_folder, '__ac_local_roles_block__', False))


class TestInitialContentForPolicylessBundleWithSingleOrgUnit(IntegrationTestCase, InitContentTestBase):

    def setUp(self):
        super(TestInitialContentForPolicylessBundleWithSingleOrgUnit, self).setUp()
        self.clear_initial_content()
        self.remove_all_org_units_except_one()

    def test_policyless_bundle_initial_content(self):
        transmogrifier = self.setup_pipeline()

        with freeze(FROZEN_NOW):
            transmogrifier(u'opengever.bundle.oggbundle')

        self.assert_inbox_created()

    def assert_inbox_created(self):
        inbox = self.portal.get('eingangskorb')
        self.assertEqual(u'opengever.inbox.inbox', inbox.portal_type)

        self.assertEqual(u'Eingangskorb', inbox.title_de)
        self.assertEqual(u'fa', IResponsibleOrgUnit(inbox).responsible_org_unit)
        self.assertEqual({
            'admin': ['Owner'],
            'fa_inbox_users': ['Contributor', 'Editor', 'Reader']},
            inbox.__ac_local_roles__)
        self.assertFalse(getattr(inbox, '__ac_local_roles_block__', False))
