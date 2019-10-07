from collections import Iterable
from collections import Mapping
from collections import OrderedDict
from datetime import datetime
from jsonschema import FormatChecker
from jsonschema import validate
from opengever.document.document import MAIL_EXTENSIONS
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

# This (almost) inverted dict is used in rare cases where we've already lost
# the information which file an item came from, but still need it
PORTAL_TYPES_TO_JSON_NAME = OrderedDict([
    ('opengever.repository.repositoryroot', 'reporoots.json'),
    ('opengever.repository.repositoryfolder', 'repofolders.json'),
    ('opengever.dossier.businesscasedossier', 'dossiers.json'),
    ('opengever.document.document', 'documents.json'),
    ('ftw.mail.mail', 'documents.json'),
])

GUID_INDEX_NAME = 'bundle_guid'


class Bundle(object):
    """An iterable OGGBundle.
    """

    def __init__(self, items, bundle_path, json_schemas=None, stats=None,
                 ingestion_settings=None, configuration=None):
        self.items = items
        self.bundle_path = bundle_path

        self.ingestion_settings = ingestion_settings
        if ingestion_settings is None:
            self.ingestion_settings = IngestionSettingsReader()()

        self.configuration = {}
        if configuration is not None:
            self.configuration = configuration

        self.json_schemas = {}
        if json_schemas is not None:
            self.json_schemas = json_schemas

        self.stats = {}
        if stats is not None:
            self.stats = stats

        self.warnings = {}
        self.errors = {}

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.bundle_path)

    def __iter__(self):
        """Yield all items of the bundle in order.
        """
        return iter(self.items)

    def get_repository_roots(self):
        roots = [item for item in self.items
                 if item['_type'] == 'opengever.repository.repositoryroot']
        return roots


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
        self._stats = {'bundle_counts_raw': {}, 'timings': {}}

    def load(self, ingestion_settings=None):
        """Load the bundle from disk and return an iterable Bundle.
        """
        self._stats['timings']['start_loading'] = datetime.now()
        self._load_items()
        configuration = self._load_configuration()
        bundle = Bundle(
            self._items, self.bundle_path, self.json_schemas, self._stats,
            ingestion_settings, configuration)
        self._display_stats(bundle)
        return bundle

    def _display_stats(self, bundle):
        log.info('')
        log.info('Raw items in bundle %r' % bundle)
        log.info('=' * 80)
        for json_name, count in bundle.stats['bundle_counts_raw'].items():
            log.info("%-20s %s" % (json_name, count))
        log.info('')

    def _load_json(self, json_name):
        json_path = os.path.join(self.bundle_path, json_name)
        log.info("Loading %s" % json_path)
        try:
            with codecs.open(json_path, 'r', 'utf-8-sig') as json_file:
                data = json.load(json_file)
        except IOError as exc:
            log.info('%s: %s, skipping' % (json_name, exc.strerror))
            return None
        return data

    def _load_configuration(self):
        config = self._load_json('configuration.json')
        return config

    def _load_items(self):
        self._items = []
        for json_name, portal_type in BUNDLE_JSON_TYPES.items():
            items = unicode2bytes(self._load_json(json_name))
            if items is None:
                continue

            self._stats['bundle_counts_raw'][json_name] = len(items)
            self._validate_schema(items, json_name)
            for item in items:
                # Apply required preprocessing to items (in-place)
                ItemPreprocessor(item, json_name).process()
                self._items.append(item)

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


class ItemPreprocessor(object):
    """A preprocessor that transforms items *in place*.

    This applies transformations that are required for the items to suit
    internal needs dictated by implementation details.

    This also serves as a compatibility layer that translates between the
    public facing OGGBundle format and the exact internal format items need
    to follow in order for "things to just work", without littering other
    parts of the codebase with conditionals for handling special cases.

    Transformations done here should be kept to a minimum, and when possible
    and appropriate, should be pushed back to the public facing OGGBundle
    specification and/or schemas.
    """

    def __init__(self, item, json_name):
        self.item = item
        self.json_name = json_name

    def process(self):
        self._set_portal_type()
        self._strip_extension_from_title()
        self._preprocess_workflow_state()

    def _set_portal_type(self):
        """Set the appropriate portal type for items.

        Determine what portal_type an item should be, based on the name of
        the JSON file it's been read from.
        """
        # Default to setting type based on which JSON file the item came from
        _type = BUNDLE_JSON_TYPES[self.json_name]

        # Mails however need a bit of special love
        if self.json_name == 'documents.json':
            filepath = self.item['filepath']

            if self._is_mail_type(filepath):
                _type = 'ftw.mail.mail'

        self.item['_type'] = _type

    def _is_mail_type(self, filepath):
        """Return whether file extension is something we consider a mail."""

        if filepath is None:
            return False

        return os.path.splitext(filepath)[-1] in MAIL_EXTENSIONS

    def _strip_extension_from_title(self):
        """Strip extension from title if present.

        Otherwise we'd end up with the extension in the final title, and twice
        in the filename derived from the title.
        """
        if self.json_name == 'documents.json':
            title = self.item['title']
            basename, ext = os.path.splitext(title)
            if self.item['filepath'].lower().endswith(ext.lower()):
                # Only strip what looks like a file extension from title if
                # filename ends with the same extension
                self.item['title'] = basename
                self.item['_original_filename'] = title

    def _preprocess_workflow_state(self):
        """Remove or map workflow state in items to suit internal needs.

        For types with only a single supported workflow-state, drop
        `review_state` entirely.
        """
        if self.json_name == 'documents.json':
            # We don't support creating documents (or mails) in any other state
            # than their initial state. So we drop the review_state entirely,
            # because it would be their initial state anyway, and therefore
            # avoid an unnecessary invocation of wftool.setStatusOf().
            self.item.pop('review_state', None)


class IngestionSettingsReader(object):
    """Read bundle ingestion related settings from a JSON file.

    These settings contain parameters that are relevant for the bundle import
    process, but are not part of the configuration parameters associated with
    the bundle. They tend to vary depending on what environment the bundle
    import is performed on.
    """

    def __init__(self, settings_path=None):
        self.settings_path = settings_path
        if not settings_path:
            self.settings_path = self.DEFAULT_SETTINGS_PATH

    DEFAULT_SETTINGS_PATH = '~/.opengever/bundle_ingestion/settings.json'

    def __call__(self):
        settings_path = os.path.expanduser(self.settings_path)
        try:
            with open(settings_path) as settings_file:
                settings = json.load(settings_file)
        except IOError:
            log.info('No ingestion settings found at %s' % settings_path)
            return {}
        return settings


def unicode2bytes(data):
    """Converts unicode strings to byte strings."""
    if isinstance(data, unicode):
        return data.encode('utf8')
    elif isinstance(data, str):
        return data
    elif isinstance(data, Mapping):
        return type(data)(map(unicode2bytes, data.iteritems()))
    elif isinstance(data, Iterable):
        return type(data)(map(unicode2bytes, data))
    else:
        return data
