from opengever.bundle.loader import BundleLoader
from opengever.bundle.tests.helpers import get_pt
from opengever.bundle.tests.helpers import get_title
from pkg_resources import resource_filename
from unittest2 import TestCase


class TestBundleLoader(TestCase):

    def load_bundle(self):
        bundle_path = resource_filename(
            'opengever.bundle.tests', 'assets/basic.oggbundle')

        bundle = BundleLoader(bundle_path)
        return list(bundle)

    def test_loads_correct_number_of_items(self):
        items = self.load_bundle()
        self.assertEqual(8, len(items))

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
             ('document', u'Entlassung Hanspeter M\xfcller')],
            [(get_pt(i), get_title(i)) for i in items])

    def test_inserts_portal_type(self):
        items = self.load_bundle()
        self.assertEqual([
            ('businesscasedossier', u'Dossier Vreni Meier'),
            ('businesscasedossier', u'Hanspeter M\xfcller'),
            ('document', u'Bewerbung Hanspeter M\xfcller'),
            ('document', u'Entlassung Hanspeter M\xfcller'),
            ('repositoryfolder', u'Organigramm, Prozesse'),
            ('repositoryfolder', u'Organisation'),
            ('repositoryfolder', u'Personal'),
            ('repositoryroot', u'Ordnungssystem')],
            sorted([(get_pt(i), get_title(i)) for i in items]))
