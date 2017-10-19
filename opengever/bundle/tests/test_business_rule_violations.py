from collective.transmogrifier.transmogrifier import Transmogrifier
from datetime import datetime
from ftw.testing import freeze
from opengever.base.security import elevated_privileges
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api
from StringIO import StringIO
from zope.annotation import IAnnotations
import logging


FROZEN_NOW = datetime(2016, 12, 20, 9, 40)


class TestBusinessRuleViolations(FunctionalTestCase):

    def setUp(self):
        # Capture logging output for test assertions
        self.log = StringIO()
        self.logger = logging.getLogger('opengever.bundle.constructor')
        self.logger.setLevel(logging.DEBUG)

        self.handler = logging.StreamHandler(self.log)
        self.logger.addHandler(self.handler)

        super(TestBusinessRuleViolations, self).setUp()

    def tearDown(self):
        super(TestBusinessRuleViolations, self).tearDown()
        self.logger.removeHandler(self.handler)

    def test_oggbundle_transmogrifier(self):
        # this is a bit hackish, but since builders currently don't work in
        # layer setup/teardown and isolation of database content is ensured
        # on a per test level we abuse just one test to setup the pipeline and
        # test its data.

        # load pipeline
        # XXX move this to a layer
        self.grant("Manager")

        transmogrifier = Transmogrifier(api.portal.get())
        IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = resource_filename(
            'opengever.bundle.tests',
            'assets/business_rule_violations.oggbundle')

        # We need to add documents to dossiers that have already been created
        # in the 'closed' state, which isn't allowed for anyone except users
        # inheriting from `UnrestrictedUser` -> we need elevated privileges
        with freeze(FROZEN_NOW), elevated_privileges():
            transmogrifier(u'opengever.bundle.oggbundle')

        # test content creation
        # XXX use separate test-cases based on a layer
        root = self.assert_repo_root_created()
        self.assert_deeply_nested_repo_folder_created(root)

        folder = root.restrictedTraverse(
            'ordnungsposition-1/ordnungsposition-1.1')
        self.assert_deeply_nested_subdossier_created(folder)
        self.assert_resolved_dossier_with_violations_created(folder)
        self.assert_disallowed_subobject_type_not_created(root)

    def assert_repo_root_created(self):
        root = self.portal.get('ordnungssystem-a')
        self.assertEqual('Ordnungssystem A', root.Title())
        return root

    def assert_deeply_nested_repo_folder_created(self, root):
        folder = root.restrictedTraverse(
            'ordnungsposition-2-nesting-depth-violations-inside/'
            'ordnungsposition-2.1/'
            'ordnungsposition-2-1.1/'
            'ordnungsposition-2-1-1-1-violates-max-nesting-depth'
        )
        self.assertEqual(
            '2.1.1.1. Ordnungsposition 2.1.1.1 (violates max nesting depth)',
            folder.Title())

        return folder

    def assert_deeply_nested_subdossier_created(self, folder):
        subdossier = folder.restrictedTraverse(
            'dossier-1/'
            'dossier-2/'
            'dossier-3/'
            'dossier-4'
        )
        self.assertEqual(
            'Subdossier 1.1-1.1.1.1 (violating max nesting depth)',
            subdossier.Title())

        return subdossier

    def assert_resolved_dossier_with_violations_created(self, folder):
        dossier = folder.restrictedTraverse('dossier-5')
        subdossier = dossier.restrictedTraverse('dossier-7')

        self.assertEqual(
            'Dossier 1.1-2 (resolved, constraint violations inside)',
            dossier.Title())

        self.assertEqual(
            u'dossier-state-resolved',
            api.content.get_state(dossier))

        self.assertEqual(
            u'dossier-state-active',
            api.content.get_state(subdossier))

        document = dossier.restrictedTraverse('document-1')
        self.assertEqual(
            'Loose Document outside subdossier (in resolved dossier)',
            document.Title())

        return dossier

    def assert_disallowed_subobject_type_not_created(self, root):
        folder = root.restrictedTraverse('ordnungsposition-1')
        subobject_types = [o.portal_type for o in folder.objectValues()]

        self.assertNotIn('opengever.document.document', subobject_types)

        self.assertIn(
            'Could not create object at '
            'ordnungssystem-a/ordnungsposition-1 with guid '
            'GUID-document-A-1-disallowed-subobject-type. '
            'Disallowed subobject type: opengever.document.document',
            self.log.getvalue())
