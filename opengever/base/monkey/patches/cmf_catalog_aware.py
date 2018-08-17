from opengever.base.monkey.patching import MonkeyPatch
from opengever.base.role_assignments import RoleAssignmentManager
from Products.CMFCore.utils import _getAuthenticatedUser
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import noLongerProvides

from plone.indexer.interfaces import IIndexer
from Products.Archetypes.config import TOOL_NAME
from Products.Archetypes.utils import isFactoryContained
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces._content import ICatalogAware
from Products.CMFCore.utils import getToolByName
from zope.component import queryMultiAdapter


class IDisableCatalogIndexing(Interface):
    """Marker-interface to disable the catalog
    indexing functions.

    If this interface is provided by the request, all the
    catalog-index-methods will be disabled.

    Use the DeactivatedCatalogIndexing contextmanager to
    get in use of this functionality.
    """


class DeactivatedCatalogIndexing(object):
    """Contextmanager: Deactivates catalog-indexing
    """
    def __enter__(self):
        alsoProvides(getRequest(), IDisableCatalogIndexing)

    def __exit__(self, exc_type, exc_val, exc_tb):
        noLongerProvides(getRequest(), IDisableCatalogIndexing)


def is_index_value_equal(old, new):
    """Compares an old and a new index value.
    If the value is of type list, it is compared as set since this usually is
    used in a KeywordIndex, where the order is not relevant.
    """
    if type(old) != type(new):
        return False
    if isinstance(old, list):
        return set(old) == set(new)
    return old == new


def is_index_up_to_date(catalog, obj, index_name):
    """Checks, whether the passed index (`index_name`) of the passed object (`obj`)
    is up to date on the passed catalog (`catalog`).
    """

    indexer = queryMultiAdapter((obj, catalog), IIndexer, name=index_name)
    if indexer is None:
        indexer = getattr(obj, index_name, None)

    if indexer is None:
        # We cannot re-generate the index data, therfore we
        # act as if it is outdated
        return False

    else:
        path = '/'.join(obj.getPhysicalPath())
        rid = catalog.getrid(path)
        if rid is None:
            # the object was not yet indexed
            return False

        indexed_values = catalog.getIndexDataForRID(catalog.getrid(path))
        value_before = indexed_values.get(index_name, None)
        value_after = indexer()
        if not is_index_value_equal(value_before, value_after):
            return False

    return True


def recursive_index_security(catalog, obj):
    """This function reindexes the security indexes for an object in a specific catalog
    recursively.
    It does this by walking down the tree and checking on every object whether a
    the security indexes are already up to date.
    If the security indexes are already up to date, it stops walking down the tree.
    The aim of stopping to walk down is to improve the performance drastically on
    large trees.
    The expectation is that if a children is up to date but the parent wasnt, the
    reason is usally that the children does not inherit the relevant values (for
    example it does not inherit the View permission) and thus the grand-children will
    also not change, so we can abort wakling down the path.
    """
    indexes_to_update = []

    # Since objectValues returns all objects, including placefulworkflow policy
    # objects, we have to check if the object is Catalog aware.
    if not ICatalogAware.providedBy(obj):
        return

    for index_name in obj._cmf_security_indexes:
        if not is_index_up_to_date(catalog, obj, index_name):
            indexes_to_update.append(index_name)

    if len(indexes_to_update) > 0:
        obj.reindexObject(idxs=indexes_to_update)

        # We assume that if the parent is up to date, all children are too.
        # This basically only walks into the tree untill an object is up to date -
        # usually because it does not inherit the security relevant thigns - and then
        # stops.
        for subobj in obj.objectValues():
            recursive_index_security(catalog, subobj)


class PatchCMFCatalogAware(MonkeyPatch):
    """Patch the Products.CMFCore.CMFCatalogAware indexObject, reindexObject
    and unindexObject methods.

    This patch is deactivated by default and can be activated through
    the DeactivatedCatalogIndexing context manager:

    >>> with DeactivatedCatalogIndexing():
    ...     object.reindexObject  # Does nothing
    ...     object.unindexObject  # Does nothing
    ...     object.indexObject  # Does nothing

    If the patch is activated, it skips the catalog index-methods.

    What's the motivation behind this patch?

    While creating an object, the object will be reindexed up to 4 times.
    This behavior takes a lot of time and is not performance-friendly. Creating
    one object through the web might be not a performance issue. But in several
    parts of the GEVER-system we're creating a lot of content programatically
    (i.e. dossiertemplates).

    To improve the performance in that case, you can decativate the index-methods
    and do it manually at the end of your tasks.
    """

    def __call__(self):
        def _is_indexing_disabled():
            return IDisableCatalogIndexing.providedBy(getRequest())

        def indexObject(self):
            if _is_indexing_disabled():
                # do nothing if indexing is disabled
                return
            return original_indexObject(self)

        def unindexObject(self):
            if _is_indexing_disabled():
                # do nothing if indexing is disabled
                return
            return original_unindexObject(self)

        def reindexObject(self, idxs=[]):
            if _is_indexing_disabled():
                # do nothing if indexing is disabled
                return
            return original_reindexObject(self, idxs)

        def reindexObjectSecurity(self, skip_self=False):
            """update security information in all registered catalogs.
            """
            if isFactoryContained(self):
                return
            at = getToolByName(self, TOOL_NAME, None)
            if at is None:
                return

            catalogs = [c for c in at.getCatalogsByType(self.meta_type)
                        if ICatalogTool.providedBy(c)]

            for catalog in catalogs:
                recursive_index_security(catalog, self)


        from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
        locals()['__patch_refs__'] = False
        original_indexObject = CMFCatalogAware.indexObject
        original_unindexObject = CMFCatalogAware.unindexObject
        original_reindexObject = CMFCatalogAware.reindexObject
        self.patch_refs(CMFCatalogAware, 'indexObject', indexObject)
        self.patch_refs(CMFCatalogAware, 'unindexObject', unindexObject)
        self.patch_refs(CMFCatalogAware, 'reindexObject', reindexObject)
        self.patch_refs(CMFCatalogAware, 'reindexObjectSecurity', reindexObjectSecurity)


class PatchCMFCatalogAwareHandlers(MonkeyPatch):
    """Customize `handleDynamicTypeCopiedEvent` to use RoleAssignmentManager
    instead of directly delete local roles
    """

    def __call__(self):

        def handleDynamicTypeCopiedEvent(ob, event):
            # Make sure owner local role is set after pasting
            # The standard Zope mechanisms take care of executable ownership
            current_user = _getAuthenticatedUser(ob)
            if current_user is None:
                return

            current_user_id = current_user.getId()
            if current_user_id is not None:

                # Customization
                RoleAssignmentManager(ob).clear_all()
                # end customization

                ob.manage_setLocalRoles(current_user_id, ['Owner'])

        from Products.CMFCore import CMFCatalogAware
        self.patch_refs(CMFCatalogAware,
                        'handleDynamicTypeCopiedEvent',
                        handleDynamicTypeCopiedEvent)
