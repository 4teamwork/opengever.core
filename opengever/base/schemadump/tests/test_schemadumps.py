from opengever.base.schemadump.config import SCHEMA_DUMPS_DIR
from opengever.base.schemadump.schema import GEVER_SQL_TYPES
from opengever.base.schemadump.schema import GEVER_TYPES
from opengever.base.schemadump.schema import GEVER_TYPES_TO_OGGBUNDLE_TYPES
from opengever.base.schemadump.schema import JSONSchemaBuilder
from opengever.base.schemadump.schema import OGGBundleJSONSchemaBuilder
from opengever.base.utils import pretty_json
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
        for portal_type in GEVER_TYPES + GEVER_SQL_TYPES:
            builder = JSONSchemaBuilder(portal_type)
            current_schema = builder.build_schema().serialize()
            filename = '%s.schema.json' % portal_type
            dump_path = pjoin(self.schema_dumps_dir, filename)

            with open(dump_path) as dump_file:
                existing_schema = json.load(dump_file)

            self.assertDictEqual(
                existing_schema,
                json.loads(pretty_json(current_schema)),
                '\n\nError: JSON schema dumps for %s have changed '
                '(see diff  above), please run bin/instance dump_schemas and '
                'commit the modified schema files together with '
                'your changes.' % dump_path)

    def test_schema_dumps_for_oggbundles(self):
        for portal_type, short_name in GEVER_TYPES_TO_OGGBUNDLE_TYPES.items():
            builder = OGGBundleJSONSchemaBuilder(portal_type)
            current_schema = builder.build_schema().serialize()
            filename = '%ss.schema.json' % short_name
            dump_path = pjoin(self.oggbundle_schema_dumps_dir, filename)

            with open(dump_path) as dump_file:
                existing_schema = json.load(dump_file)

            self.assertDictEqual(
                existing_schema,
                json.loads(pretty_json(current_schema)),
                '\n\nError: JSON schema dumps for %s have changed '
                '(see diff  above), please run bin/instance dump_schemas and '
                'commit the modified schema files together with '
                'your changes.' % dump_path)
