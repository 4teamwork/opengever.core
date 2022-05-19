from opengever.base import _
from opengever.base.monkey.patching import MonkeyPatch
from opengever.base.role_assignments import RoleAssignmentManager
from plone import api
from Products.CMFCore.utils import _getAuthenticatedUser
from zope.globalrequest import getRequest


class DeactivatedCatalogIndexing(object):
    """Contextmanager: Deactivates catalog-indexing
    """
    def __init__(self):
        self.catalog_patch = PatchCMFCatalogAware()

    def __enter__(self):
        self.catalog_patch.patch()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.catalog_patch.unpatch()


class CatalogAlreadyPatched(Exception):
    """Will be raised if we try to patch the catalog indexing methods
    more than once.
    """


class PatchCMFCatalogAware(MonkeyPatch):
    """Patch the Products.CMFCore.CMFCatalogAware indexObject, reindexObject
    and unindexObject methods.

    This patch is not applied by default and can be activated
    through the DeactivatedCatalogIndexing context manager:

    >>> with DeactivatedCatalogIndexing():
    ...     object.reindexObject  # Does nothing
    ...     object.unindexObject  # Does nothing
    ...     object.indexObject  # Does nothing

    If the patch is activated, it skips the catalog index-methods. The patch
    gets removed when exiting the context manager.

    Note that the unpatch method needs to be called on the same
    instance of this class which was used to apply the patch.

    What's the motivation behind this patch?

    While creating an object, the object will be reindexed up to 4 times.
    This behavior takes a lot of time and is not performance-friendly. Creating
    one object through the web might be not a performance issue. But in several
    parts of the GEVER-system we're creating a lot of content programatically
    (i.e. dossiertemplates).

    To improve the performance in that case, you can decativate the index-methods
    and do it manually at the end of your tasks.
    """

    def indexObject(self):
        return

    def unindexObject(self):
        return

    def reindexObject(self, idxs=[]):
        return

    def __init__(self):
        self.original_indexing_methods = {}

    def patch(self):

        if self.is_already_applied():
            raise CatalogAlreadyPatched()

        from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
        locals()['__patch_refs__'] = False
        self.original_indexing_methods['indexObject'] = CMFCatalogAware.indexObject
        self.original_indexing_methods['unindexObject'] = CMFCatalogAware.unindexObject
        self.original_indexing_methods['reindexObject'] = CMFCatalogAware.reindexObject
        self.patch_refs(CMFCatalogAware, 'indexObject', self.indexObject)
        self.patch_refs(CMFCatalogAware, 'unindexObject', self.unindexObject)
        self.patch_refs(CMFCatalogAware, 'reindexObject', self.reindexObject)

    def is_already_applied(self):
        from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
        return (
            CMFCatalogAware.indexObject.__func__ is self.indexObject.__func__ and
            CMFCatalogAware.reindexObject.__func__ is self.reindexObject.__func__ and
            CMFCatalogAware.unindexObject.__func__ is self.unindexObject.__func__
            )

    def unpatch(self):
        from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
        locals()['__patch_refs__'] = False
        self.patch_refs(CMFCatalogAware, 'indexObject',
                        self.original_indexing_methods.pop('indexObject'))
        self.patch_refs(CMFCatalogAware, 'unindexObject',
                        self.original_indexing_methods.pop('unindexObject'))
        self.patch_refs(CMFCatalogAware, 'reindexObject',
                        self.original_indexing_methods.pop('reindexObject'))


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
                are_all_local_roles_deleted = RoleAssignmentManager(ob)\
                    .update_local_roles_after_copying(current_user_id)
                if not are_all_local_roles_deleted:
                    message = _(
                        'local_roles_copied',
                         default=u"Some local roles were copied with the objects")
                    api.portal.show_message(message=message,
                                            request=getRequest(),
                                            type='info')
                # end customization

        from Products.CMFCore import CMFCatalogAware
        self.patch_refs(CMFCatalogAware,
                        'handleDynamicTypeCopiedEvent',
                        handleDynamicTypeCopiedEvent)
