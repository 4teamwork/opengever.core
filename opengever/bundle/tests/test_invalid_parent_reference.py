from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.bundle.sections.resolveguid import ReferenceNumberNotFound
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api
from zope.annotation import IAnnotations


class TestInvalidParentReference(FunctionalTestCase):

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
            'assets/invalid_parent_reference.oggbundle')

        with self.assertRaises(ReferenceNumberNotFound) as cm:
            transmogrifier(u'opengever.bundle.oggbundle')

        self.assertEqual(
            "Couldn't find container with reference number Client1 7.7.7 "
            "(referenced as parent by item by GUID GUID-dossier-A-7.7.7-1 )",
            cm.exception.message)
