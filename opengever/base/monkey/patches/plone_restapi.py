from opengever.base.monkey.patching import MonkeyPatch


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
