from collections import OrderedDict
from jsonschema import FormatChecker
from jsonschema import validate
from pkg_resources import resource_filename as rf
import codecs
import json
import logging
import os


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


BUNDLE_JSON_TYPES = OrderedDict([
    ('reporoots.json', 'opengever.repository.repositoryroot'),
    ('repofolders.json', 'opengever.repository.repositoryfolder'),
    ('dossiers.json', 'opengever.dossier.businesscasedossier'),
    ('documents.json', 'opengever.document.document'),   # document or mail
])


class BundleLoader(object):
    """Loads an OGGBundle from the filesystem and yields the containing items
    in proper order.

    The loader also takes care of inserting the appropriate portal_type for
    each item.

    Upon loading the bundle, the JSON files that are present will be validated
    against their respective JSON schemas, which are expected to be found in
    opengever.bundle.schemas and to be up to date.
    """

    def __init__(self, bundle_path):
        self.bundle_path = bundle_path
        self.json_schemas = self.load_schemas()

        self.load_items()

    def load_items(self):
        self.items = []
        for json_name, portal_type in BUNDLE_JSON_TYPES.items():
            json_path = os.path.join(self.bundle_path, json_name)

            try:
                with codecs.open(json_path, 'r', 'utf-8-sig') as json_file:
                    items = json.load(json_file)
            except IOError as exc:
                log.info('%s: %s, skipping' % (json_name, exc.strerror))
                continue

            self.validate_schema(items, json_name)
            for item in items:
                item['_type'] = self.determine_portal_type(json_name, item)
                self.items.append(item)

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

    def validate_schema(self, items, json_name):
        schema = self.json_schemas[json_name]
        # May raise jsonschema.ValidationError
        validate(items, schema, format_checker=FormatChecker())

    def determine_portal_type(self, json_name, item):
        """Determine what portal_type an item should be, based on the name of
        the JSON file it's been read from.
        """
        if json_name == 'documents.json':
            filepath = item['filepath']
            if filepath is not None and filepath.endswith('.eml'):
                return 'ftw.mail.mail'
            return 'opengever.document.document'
        return BUNDLE_JSON_TYPES[json_name]

    def __iter__(self):
        """Yield all items of the bundle in order.
        """
        for item in self.items:
            yield item
