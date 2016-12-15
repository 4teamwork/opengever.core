from collections import OrderedDict
from jsonschema import FormatChecker
from jsonschema import validate
from opengever.bundle.exceptions import DuplicateGUID
from opengever.bundle.exceptions import MissingGUID
from opengever.bundle.exceptions import MissingParent
import codecs
import json
import os


BUNDLE_JSON_TYPES = OrderedDict([
    ('reporoots.json', 'opengever.repository.repositoryroot'),
    ('repofolders.json', 'opengever.repository.repositoryfolder'),
    ('dossiers.json', 'opengever.dossier.businesscasedossier'),
    ('documents.json', 'opengever.document.document'),   # document or mail
])


class BundleLoader(object):
    """Loads an OGGBundle from the filesystem, validates its JSON files against
    the provided schemas, and yields the containing items in proper order.

    The loader also takes care of inserting the appropriate portal_type for
    each item.

    Expects a dictionary of JSON schemas in the form of a {json_name: schema}
    mapping.
    """

    def __init__(self, bundle_path, json_schemas):
        self.bundle_path = bundle_path
        self.json_schemas = json_schemas

        # Load flat item list from JSON files and validate schemas
        _items = self._load_items()

        # Register items in a guid -> item mapping
        self.item_by_guid = OrderedDict()
        self._register_items(_items)

        # Build tree that represents containment
        self.tree = self._build_tree()

        # Build canonical flat item list in proper order
        self._items = list(self._visit_in_pre_order(self.tree))

    def _load_items(self):
        """Read items from JSON files and validate their schemas.
        """
        for json_name, portal_type in BUNDLE_JSON_TYPES.items():
            json_path = os.path.join(self.bundle_path, json_name)

            with codecs.open(json_path, 'r', 'utf-8-sig') as json_file:
                items = json.load(json_file)

            self._validate_schema(items, json_name)
            for item in items:
                item['_type'] = self._determine_portal_type(json_name, item)
                yield item

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

    def _register_items(self, items):
        """Register all items by their guid."""
        for item in items:
            if 'guid' not in item:
                raise MissingGUID(item)

            guid = item['guid']
            if guid in self.item_by_guid:
                raise DuplicateGUID(guid)

            self.item_by_guid[guid] = item

    def _build_tree(self):
        """Build a tree from the flat list of items.

        Register all items with their parents.
        """
        roots = []
        for item in self.item_by_guid.values():
            parent_guid = item.get('parent_guid')
            if parent_guid:
                parent = self.item_by_guid.get(parent_guid)
                if not parent:
                    raise MissingParent(parent_guid)
                children = parent.setdefault('_children', [])
                children.append(item)
            else:
                roots.append(item)
        return roots

    def _visit_in_pre_order(self, tree):
        """Visit tree of items depth first, always yield parent before its
        children.

        """
        for item in tree:
            children = item.get('_children', [])
            yield item

            for child in self._visit_in_pre_order(children):
                yield child

    def __iter__(self):
        """Yield all items of the bundle in order.
        """
        return iter(self._items)
