from collections import OrderedDict
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


log = logging.getLogger('opengever.bundle.resolveguid')
log.setLevel(logging.INFO)


class MissingGuid(Exception):
    pass


class DuplicateGuid(Exception):
    pass


class MissingParent(Exception):
    pass


class ResolveGUIDSection(object):
    """Resolve and validate GUIDs.

    Each item must define a globally unique identifier (GUID) wich is used as
    identifier while importing an oggbundle. The format of this id can be
    chosen freely.

    Yield items in an order that guarantees that parents are always positioned
    before their children. This is achieved by building a temporary tree, then
    re-yielding the children in pre-order.

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
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]

        self.bundle.item_by_guid = OrderedDict()

    def __iter__(self):
        self.register_items()
        roots = self.build_tree()
        for node in self.visit_in_pre_order(
                roots, level=1, previous_type='Portal'):
            yield node

    def register_items(self):
        """Register all items by their guid."""

        for item in self.previous:
            if 'guid' not in item:
                raise MissingGuid(item)

            guid = item['guid']
            if guid in self.bundle.item_by_guid:
                raise DuplicateGuid(guid)

            self.bundle.item_by_guid[guid] = item

    def build_tree(self):
        """Build a tree from the flat list of items.

        Register all items with their parents.
        """
        roots = []
        for item in self.bundle.item_by_guid.values():
            parent_guid = item.get('parent_guid', None)
            if parent_guid:
                parent = self.bundle.item_by_guid.get(parent_guid)
                if not parent:
                    msg = "%r (referenced by GUID %r)" % (
                        parent_guid, item['guid'])
                    raise MissingParent(msg)
                children = parent.setdefault('_children', [])
                children.append(item)
            else:
                roots.append(item)
        return roots

    def visit_in_pre_order(self, items, level, previous_type):
        """Visit list of items depth first, always yield parent before its
        children.

        In addition, keep track of the nesting depth of objects of the *same
        type* - this is used for validation in a later section.
        """
        for item in items:
            type_ = item.get('_type')

            # Type of nested folderish items changed - reset nesting depth
            if previous_type != type_:
                level = 1

            item['_nesting_depth'] = level
            children = item.pop('_children', [])
            yield item

            for child in self.visit_in_pre_order(
                    children, level + 1, type_):
                yield child
