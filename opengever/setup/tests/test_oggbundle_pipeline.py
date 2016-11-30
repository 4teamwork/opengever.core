from collective.transmogrifier.transmogrifier import Transmogrifier
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_filename
from plone import api


class TestOggBundlePipeline(FunctionalTestCase):

    def test_oggbundle_transmogrifier(self):
        # this is a bit hackish, but since builders currently don't work in
        # layer setup/teardown and isolation of database content is ensured
        # on a per test level we abuse just one test to setup the pipeline and
        # test its data.
        # i'd like to this in a fixture instead, but as things are for now
        # we depend on content

        # load pipeline
        self.grant("Manager")
        user, org_unit, admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        transmogrifier = Transmogrifier(api.portal.get())
        transmogrifier.bundle_dir = resource_filename(
            'opengever.setup.tests', 'assets/oggbundle')
        transmogrifier(u'opengever.setup.oggbundle')

