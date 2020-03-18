from opengever.base.interfaces import ISQLObjectWrapper
from opengever.base.monkey.patching import MonkeyPatch
from plone.rest.interfaces import IService
from Products.CMFCore.interfaces import IContentish
from zope.component import queryMultiAdapter
from ZPublisher.BaseRequest import DefaultPublishTraverse


def safe_utf8(to_utf8):
    if isinstance(to_utf8, unicode):
        to_utf8 = to_utf8.encode('utf-8')
    return to_utf8


class PatchPloneRestAPIOrdering(MonkeyPatch):
    """Temporary patch for ordering stored as unicode instead of bytestring in
    plone.restapi. Can go away as soon as we have a plone.restapi with
    https://github.com/plone/plone.restapi/pull/828.
    """

    def __call__(self):
        from plone.restapi.deserializer.mixins import OrderingMixin

        def reorderItems(self, obj_id, delta, subset_ids):
            """Encode any unicode-ids as ascii to prevent mixed type ids."""
            obj_id = safe_utf8(obj_id)
            if subset_ids:
                subset_ids = [safe_utf8(id_) for id_ in subset_ids]

            return original_reorderItems(self, obj_id, delta, subset_ids)

        locals()['__patch_refs__'] = False
        original_reorderItems = OrderingMixin.reorderItems
        self.patch_refs(OrderingMixin, 'reorderItems', reorderItems)


class PatchPloneRESTWrapper(MonkeyPatch):
    """We need to patch plone.rest.traverse.RESTWrapper, so that traversal
    works properly for our SQL objects for which we extend traversal with
    SQLWrapperBase.
    """

    def __call__(self):
        from plone.rest.traverse import RESTWrapper

        def publishTraverse(self, request, name):
            # Try to get an object using default traversal
            adapter = DefaultPublishTraverse(self.context, request)
            try:
                obj = adapter.publishTraverse(request, name)
                if (not IContentish.providedBy(obj)
                        and not IService.providedBy(obj)
                        and not ISQLObjectWrapper.providedBy(obj)):
                    raise KeyError

            # If there's no object with the given name, we get a KeyError.
            # In a non-folderish context a key lookup results in an AttributeError.
            except (KeyError, AttributeError):
                # No object, maybe a named rest service
                service = queryMultiAdapter((self.context, request),
                                            name=request._rest_service_id + name)
                if service is None:
                    # No service, fallback to regular view
                    view = queryMultiAdapter((self.context, request), name=name)
                    if view is not None:
                        return view
                    raise
                return service
            else:
                # Wrap object to ensure we handle further traversal
                return RESTWrapper(obj, request)

        self.patch_refs(RESTWrapper, 'publishTraverse', publishTraverse)
