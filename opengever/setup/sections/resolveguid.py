from collections import OrderedDict
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from zope.interface import classProvides
from zope.interface import implements


class MissingGuid(Exception):
    pass


class DuplicateGuid(Exception):
    pass


class MissingParent(Exception):
    pass


class ResolveGUIDSection(object):
    """Resolve and validate GUIDs.

    This section also validates that:
        - each item has a guid
        - each guid is unique
        - parent pointers are valid, should they exist

    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier
        self.transmogrifier.item_by_guid = OrderedDict()

    @property
    def item_by_guid(self):
        return self.transmogrifier.item_by_guid

    def __iter__(self):
        self.register_items()
        roots = self.build_tree()

    def register_items(self):
        """Register all items by their guid."""

        for item in self.previous:
            if 'guid' not in item:
                raise MissingGuid(item)

            guid = item['guid']
            if guid in self.item_by_guid:
                raise DuplicateGuid(guid)

            self.item_by_guid[guid] = item

    def build_tree(self):
        """Build a tree from the flat list of items.

        Register all items with their parents.
        """
        roots = []
        for item in self.item_by_guid.values():
            parent_guid = item.get('parent_guid', None)
            if parent_guid:
                parent = self.item_by_guid.get(parent_guid)
                if not parent:
                    raise MissingParent(parent_guid)
                children = parent.setdefault('_children', [])
                children.append(item)
            else:
                roots.append(item)
        return roots

