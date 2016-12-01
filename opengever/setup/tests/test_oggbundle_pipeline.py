from collective.transmogrifier.transmogrifier import Transmogrifier
from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api


class TestOggBundlePipeline(FunctionalTestCase):

    use_default_fixture = False

    def test_oggbundle_transmogrifier(self):
        # this is a bit hackish, but since builders currently don't work in
        # layer setup/teardown and isolation of database content is ensured
        # on a per test level we abuse just one test to setup the pipeline and
        # test its data.

        # load pipeline
        # XXX move this to a layer
        self.grant("Manager")
        user, org_unit, admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        transmogrifier = Transmogrifier(api.portal.get())
        transmogrifier.bundle_dir = resource_filename(
            'opengever.setup.tests', 'assets/oggbundle')
        transmogrifier(u'opengever.setup.oggbundle')

        # test content creation
        # XXX use separate test-cases based on a layer
        self.assert_repo_root_created()

    def assert_repo_root_created(self):
        root = self.portal.get('ordnungssystem')
        self.assertEqual('Ordnungssystem', root.Title())
        self.assertEqual(u'Ordnungssystem', root.title_de)
        self.assertEqual(u'', root.title_fr)
        self.assertEqual('ordnungssystem', root.getId())
        self.assertEqual(date(2000, 1, 1), root.valid_from)
        self.assertEqual(date(2099, 12, 31), root.valid_until)
