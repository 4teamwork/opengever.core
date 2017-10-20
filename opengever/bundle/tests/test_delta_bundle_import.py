from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.bundle.console import add_guid_index
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api
from zope.annotation import IAnnotations


class TestDeltaBundleImport(FunctionalTestCase):

    def import_bundle(self, bundle_name):
        bundle_path = resource_filename(
            'opengever.bundle.tests',
            'assets/%s' % bundle_name)
        transmogrifier = Transmogrifier(api.portal.get())
        IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = bundle_path
        transmogrifier(u'opengever.bundle.oggbundle')

    def test_oggbundle_transmogrifier(self):
        # this is a bit hackish, but since builders currently don't work in
        # layer setup/teardown and isolation of database content is ensured
        # on a per test level we abuse just one test to setup the pipeline and
        # test its data.

        # load pipeline
        # XXX move this to a layer
        self.grant("Manager")

        # Create the 'bundle_guid' index. In production, this will be done
        # by the "bin/instance import" command in opengever.bundle.console
        add_guid_index()

        self.import_bundle('delta_base.oggbundle')
        self.import_bundle('delta.oggbundle')

        repofolder_from_base = self.portal.restrictedTraverse(
            'ordnungssystem-a/ordnungsposition-1/ordnungsposition-1.1')

        self.assertEquals(['dossier-1'], repofolder_from_base.objectIds())

        dossier = repofolder_from_base.restrictedTraverse('dossier-1')
        self.assertEqual(
            u'Dossier 1.1-1 (delta import into existing repofolder)',
            dossier.title)
