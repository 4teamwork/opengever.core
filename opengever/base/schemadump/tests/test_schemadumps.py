from opengever.base.schemadump.config import SCHEMA_DUMPS_DIR
from opengever.base.schemadump.schema import build_all_bundle_schemas
from opengever.base.schemadump.schema import build_all_gever_schemas
from opengever.testing import IntegrationTestCase
from os.path import join as pjoin
from os.path import normpath
from pkg_resources import resource_filename
import json


class TestCheckedInSchemaDumpsAreUpToDate(IntegrationTestCase):

    maxDiff = None

    @property
    def og_core_package_path(self):
        return normpath(pjoin(resource_filename('opengever.core', ''), '..', '..'))  # noqa

    @property
    def schema_dumps_dir(self):
        return pjoin(self.og_core_package_path, SCHEMA_DUMPS_DIR)

    @property
    def oggbundle_schema_dumps_dir(self):
        return pjoin(resource_filename('opengever.bundle', 'schemas/'))

    def test_schema_dumps_for_api(self):
        for filename, current_schema in build_all_gever_schemas():
            dump_path = pjoin(self.schema_dumps_dir, filename)

            with open(dump_path) as dump_file:
                existing_schema = json.load(dump_file)

            # Shove schema through dump / load in order to get rid of
            # OrderedDicts and get better diffability
            current_schema = json.loads(json.dumps(current_schema.serialize()))

            self.assertDictEqual(
                existing_schema,
                current_schema,
                '\n\nError: JSON schema dumps for %s have changed '
                '(see diff  above), please run bin/instance dump_schemas and '
                'commit the modified schema files together with '
                'your changes.' % dump_path)

    def test_schema_dumps_for_oggbundles(self):
        for filename, current_schema in build_all_bundle_schemas():
            dump_path = pjoin(self.oggbundle_schema_dumps_dir, filename)

            with open(dump_path) as dump_file:
                existing_schema = json.load(dump_file)

            self.assertDictEqual(
                existing_schema,
                current_schema.serialize(),
                '\n\nError: JSON schema dumps for %s have changed '
                '(see diff  above), please run bin/instance dump_schemas and '
                'commit the modified schema files together with '
                'your changes.' % dump_path)
