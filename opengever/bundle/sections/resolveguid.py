from collections import OrderedDict
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.bundle.loader import PORTAL_TYPES_TO_JSON_NAME
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from plone import api
from zope.annotation import IAnnotations
from zope.component import queryAdapter
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


class ReferenceNumberNotFound(Exception):
    pass


class MissingParentPointer(Exception):
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

        # Table of formatted refnums that exist in Plone
        self.bundle.existing_refnums = ()
        # Table of bundle GUIDs that exist in Plone
        self.bundle.existing_guids = ()

        # Current reference number formatter
        self.formatter = None

        self.catalog = api.portal.get_tool('portal_catalog')

        # Track stats about actual item counts (minus skipped ones)
        if 'bundle_counts_actual' not in self.bundle.stats:
            self.bundle.stats['bundle_counts_actual'] = {}

    def __iter__(self):
        self.register_items_by_guid()
        roots = self.build_tree()
        for node in self.visit_in_pre_order(
                roots, level=1, previous_type='Portal'):
            yield node

    def get_formatter(self):
        if not self.formatter:
            active_formatter = api.portal.get_registry_record(
                name='formatter', interface=IReferenceNumberSettings)
            self.formatter = queryAdapter(
                api.portal.get(), IReferenceNumberFormatter,
                name=active_formatter)

        return self.formatter

    def get_existing_refnums(self):
        index = self.catalog._catalog.indexes['reference']
        return tuple(index.uniqueValues())

    def register_items_by_guid(self):
        """Register all items by their guid."""
        # Collect existing GUIDs and reference numbers from catalog index
        self.bundle.existing_guids = self.get_all_existing_guids()
        self.bundle.existing_refnums = self.get_existing_refnums()

        for item in self.previous:
            if 'guid' not in item:
                raise MissingGuid(item)

            guid = item['guid']

            if guid in self.bundle.existing_guids:
                log.info('Skipping existing GUID %s when building tree' % guid)
                continue

            if guid in self.bundle.item_by_guid:
                raise DuplicateGuid(guid)

            self.bundle.item_by_guid[guid] = item

            parent_reference = item.get('parent_reference')
            if parent_reference is not None:
                # Item has a parent pointer via reference number
                fmt = self.get_formatter()
                formatted_parent_refnum = fmt.list_to_string(parent_reference)
                item['_formatted_parent_refnum'] = formatted_parent_refnum

        # Verify parent pointers - all referenced items/containers must exist
        for guid, item in self.bundle.item_by_guid.items():
            parent_guid = item.get('parent_guid')
            parent_reference = item.get('parent_reference')

            if parent_guid is not None:
                if not any((parent_guid in self.bundle.item_by_guid,
                            parent_guid in self.bundle.existing_guids)):
                    raise MissingParent(
                        "Couldn't find item/container with GUID %s "
                        "(referenced as parent by item by GUID %s ) in either "
                        "Plone or the bundle itself" % (parent_guid, guid))

            elif parent_reference is not None:
                formatted_refnum = item['_formatted_parent_refnum']
                if formatted_refnum not in self.bundle.existing_refnums:
                    raise ReferenceNumberNotFound(
                        "Couldn't find container with reference number %s "
                        "(referenced as parent by item by GUID %s )" % (
                            formatted_refnum, guid))

    def get_all_existing_guids(self):
        index = self.catalog._catalog.indexes['bundle_guid']
        guids = tuple(index.uniqueValues())
        return guids

    def track_actual_item_stats(self, item):
        portal_type = item['_type']
        bundle_counts_actual = self.bundle.stats['bundle_counts_actual']
        json_name = PORTAL_TYPES_TO_JSON_NAME[portal_type]
        if json_name not in bundle_counts_actual:
            bundle_counts_actual[json_name] = 0
        bundle_counts_actual[json_name] += 1

    def display_actual_stats(self):
        log.info('')
        log.info('Actual items about to be migrated')
        log.info('=' * 80)
        bundle_counts_actual = self.bundle.stats['bundle_counts_actual']
        for json_name, count in bundle_counts_actual.items():
            log.info("%-20s %s" % (json_name, count))

        log.info('')
        total = sum(self.bundle.stats['bundle_counts_actual'].values())
        log.info('About to migrate %s actual items total.' % total)
        log.info('')

    def build_tree(self):
        """Build a tree from the flat list of items.

        Register all items with their parents.
        """
        roots = []
        for item in self.bundle.item_by_guid.values():
            self.track_actual_item_stats(item)

            parent_guid = item.get('parent_guid')
            parent_reference = item.get('parent_reference')

            existing_parent_guid = parent_guid in self.bundle.existing_guids

            if parent_guid and not existing_parent_guid:
                parent_item = self.bundle.item_by_guid.get(parent_guid)
                if not parent_item:
                    msg = "%r (referenced by GUID %r)" % (
                        parent_guid, item['guid'])
                    raise MissingParent(msg)
                children = parent_item.setdefault('_children', [])
                children.append(item)

            # Not really "roots" as such, rather an item with a parent
            # that's outside the bundle tree (i.e. Plone)
            elif parent_guid and existing_parent_guid:
                roots.append(item)
            elif parent_reference is not None:
                roots.append(item)

            elif item['_type'] == 'opengever.repository.repositoryroot':
                # Repo roots are the only type without a parent pointer
                roots.append(item)
            else:
                raise MissingParentPointer(
                    "No parent pointer for item with GUID %s" % item['guid'])

        self.display_actual_stats()
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
