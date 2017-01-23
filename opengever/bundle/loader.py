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


class Bundle(object):
    """An iterable OGGBundle.
    """

    def __init__(self, items, bundle_path, json_schemas=None, stats=None):
        self.items = items
        self.bundle_path = bundle_path

        self.json_schemas = {}
        if json_schemas is not None:
            self.json_schemas = json_schemas

        self.stats = {}
        if stats is not None:
            self.stats = stats

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.bundle_path)

    def __iter__(self):
        """Yield all items of the bundle in order.
        """
        return iter(self.items)


class BundleLoader(object):
    """Loads an OGGBundle from the filesystem and yields the contained items
    in proper order.

    The loader also takes care of inserting the appropriate portal_type for
    each item.

    Upon loading the bundle, the JSON files that are present will be validated
    against their respective JSON schemas, which are expected to be found in
    opengever.bundle.schemas and to be up to date.
    """

    def __init__(self, bundle_path):
        self.bundle_path = bundle_path
        self.json_schemas = self._load_schemas()

    def load(self):
        """Load the bundle from disk and return an iterable Bundle.
        """
        self._load_items()
        bundle = Bundle(
            self._items, self.bundle_path, self.json_schemas, self._stats)
        self._display_stats(bundle)
        return bundle

    def _display_stats(self, bundle):
        log.info('')
        log.info('Stats for %r' % bundle)
        log.info('=' * 80)
        for json_name, count in bundle.stats['counts'].items():
            log.info("%-20s %s" % (json_name, count))

    def _load_items(self):
        self._items = []
        self._stats = {'counts': {}}
        for json_name, portal_type in BUNDLE_JSON_TYPES.items():
            json_path = os.path.join(self.bundle_path, json_name)

            try:
                with codecs.open(json_path, 'r', 'utf-8-sig') as json_file:
                    items = json.load(json_file)
                    self._stats['counts'][json_name] = len(items)
            except IOError as exc:
                log.info('%s: %s, skipping' % (json_name, exc.strerror))
                continue

            self._validate_schema(items, json_name)
            for item in items:
                item['_type'] = self._determine_portal_type(json_name, item)
                if json_name == 'documents.json':
                    self._strip_extension_from_title(item)
                self._items.append(item)

    def _strip_extension_from_title(self, item):
        """Strip extension from title if present. Otherwise we'd end up with
        the extension in the final title.
        """
        title = item['title']
        basename, ext = os.path.splitext(title)
        if item['filepath'].lower().endswith(ext.lower()):
            # Only strip what looks like a file extension from title if
            # filename ends with the same extension
            item['title'] = basename
            item['_original_filename'] = title
        return item

    def _load_schemas(self):
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

    def _validate_schema(self, items, json_name):
        schema = self.json_schemas[json_name]
        # May raise jsonschema.ValidationError
        validate(items, schema, format_checker=FormatChecker())

    def _determine_portal_type(self, json_name, item):
        """Determine what portal_type an item should be, based on the name of
        the JSON file it's been read from.
        """
        if json_name == 'documents.json':
            filepath = item['filepath']
            if filepath is not None and filepath.endswith('.eml'):
                return 'ftw.mail.mail'
            return 'opengever.document.document'
        return BUNDLE_JSON_TYPES[json_name]
