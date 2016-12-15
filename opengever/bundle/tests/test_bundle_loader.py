from opengever.bundle.loader import BUNDLE_JSON_TYPES
from opengever.bundle.loader import BundleLoader
from opengever.bundle.tests.helpers import get_pt
from opengever.bundle.tests.helpers import get_title
from pkg_resources import resource_filename as rf
from unittest2 import TestCase
import codecs
import json
import jsonschema
import os


def get_bundle_path(bundle_name):
    return rf('opengever.bundle.tests', 'assets/%s' % bundle_name)


class TestBundleLoader(TestCase):

    def load_schemas(self):
        schema_dir = rf('opengever.bundle', 'schemas/')
        schemas = {}
        filenames = os.listdir(schema_dir)
        for schema_filename in filenames:
            short_name = schema_filename.replace('.schema.json', '')
            if '%s.json' % short_name in BUNDLE_JSON_TYPES:
                schema_path = os.path.join(schema_dir, schema_filename)

                with codecs.open(schema_path, 'r', 'utf-8-sig') as schema_file:
                    schema = json.load(schema_file)
                schemas['%s.json' % short_name] = schema
        return schemas

    def load_bundle(self, bundle_path=None):
        if not bundle_path:
            bundle_path = get_bundle_path('basic.oggbundle')
        schemas = self.load_schemas()
        bundle = BundleLoader(bundle_path, schemas)
        return list(bundle)

    def test_loads_correct_number_of_items(self):
        items = self.load_bundle()
        self.assertEqual(8, len(items))

    def test_loads_items_in_correct_order(self):
        items = self.load_bundle()
        # TODO: A "correct order" at this point is any order that satisfies
        # the "parents before children" constraint.
        self.assertEqual([
            ('repositoryroot', u'Ordnungssystem'),
            ('repositoryfolder', u'Organisation'),
            ('repositoryfolder', u'Personal'),
            ('businesscasedossier', u'Dossier Vreni Meier'),
            ('businesscasedossier', u'Hanspeter M\xfcller'),
            ('document', u'Bewerbung Hanspeter M\xfcller'),
            ('document', u'Entlassung Hanspeter M\xfcller'),
            ('repositoryfolder', u'Organigramm, Prozesse')],
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

    def test_validates_schemas(self):
        bundle_path = get_bundle_path('schema_violation.oggbundle')

        with self.assertRaises(jsonschema.ValidationError):
            self.load_bundle(bundle_path)
