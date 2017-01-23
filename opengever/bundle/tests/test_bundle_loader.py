from opengever.bundle.loader import BundleLoader
from opengever.bundle.tests.helpers import get_portal_type
from opengever.bundle.tests.helpers import get_title
from pkg_resources import resource_filename as rf
from unittest2 import TestCase
import jsonschema


def get_bundle_path(bundle_name):
    return rf('opengever.bundle.tests', 'assets/%s' % bundle_name)


class TestBundleLoader(TestCase):

    def load_bundle(self, bundle_path=None):
        if not bundle_path:
            bundle_path = get_bundle_path('basic.oggbundle')
        loader = BundleLoader(bundle_path)
        bundle = loader.load()
        return list(bundle)

    def test_loads_correct_number_of_items(self):
        items = self.load_bundle()
        self.assertEqual(9, len(items))

    def test_loads_items_in_correct_order(self):
        items = self.load_bundle()
        self.assertEqual(
            [('repositoryroot', u'Ordnungssystem'),
             ('repositoryfolder', u'Personal'),
             ('repositoryfolder', u'Organigramm, Prozesse'),
             ('repositoryfolder', u'Organisation'),
             ('businesscasedossier', u'Dossier Vreni Meier'),
             ('businesscasedossier', u'Hanspeter M\xfcller'),
             ('document', u'Bewerbung Hanspeter M\xfcller'),
             ('document', u'Entlassung Hanspeter M\xfcller'),
             ('mail', u'Ein Mail')],
            [(get_portal_type(i), get_title(i)) for i in items])

    def test_inserts_portal_type(self):
        items = self.load_bundle()
        self.assertEqual([
            ('businesscasedossier', u'Dossier Vreni Meier'),
            ('businesscasedossier', u'Hanspeter M\xfcller'),
            ('document', u'Bewerbung Hanspeter M\xfcller'),
            ('document', u'Entlassung Hanspeter M\xfcller'),
            ('mail', u'Ein Mail'),
            ('repositoryfolder', u'Organigramm, Prozesse'),
            ('repositoryfolder', u'Organisation'),
            ('repositoryfolder', u'Personal'),
            ('repositoryroot', u'Ordnungssystem')],
            sorted([(get_portal_type(i), get_title(i)) for i in items]))

    def test_validates_schemas(self):
        bundle_path = get_bundle_path('schema_violation.oggbundle')

        with self.assertRaises(jsonschema.ValidationError):
            self.load_bundle(bundle_path)

    def test_skips_missing_files_gracefully(self):
        bundle = self.load_bundle(get_bundle_path('partial.bundle'))
        self.assertEqual(1, len(bundle))
