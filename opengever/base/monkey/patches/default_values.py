from copy import deepcopy
from opengever.base.monkey.patching import MonkeyPatch
from plone.dexterity.content import _marker
from zope.schema.interfaces import IContextAwareDefaultFactory


def _default_from_schema(context, schema, fieldname):
    """Helper to look up default value of a field

    (taken from plone.dexterity.utils 2.3.0 )
    """
    if schema is None:
        return _marker
    field = schema.get(fieldname, None)
    if field is None:
        return _marker
    if IContextAwareDefaultFactory.providedBy(
            getattr(field, 'defaultFactory', None)
    ):
        bound = field.bind(context)
        return deepcopy(bound.default)
    else:
        return deepcopy(field.default)
    return _marker


class PatchDexterityContentGetattr(MonkeyPatch):
    """Patch DexterityContent.__getattr__ to correctly fall back to defaults
    from behavior schemas.

    Rationale: The implementation in plone.dexterity 2.1.x grabs
    *marker interfaces* from SCHEMA_CACHE.subtypes() for behaviors that have
    them, instead of their schema interfaces.

    If there's a fallback logic in place (and we can't get rid of
    it), it should at least work consistently.

    The __getattr__ below is an exact copy of DexterityContent.__getattr__
    from plone.dexterity == 2.3.0. That version doesn't use SCHEMA_CACHE at
    all for behavior schemata, and so avoids using the questionable
    SCHEMA_CACHE.subtypes(). This was fixed in plone/plone.dexterity#21 by
    @jensens as part of a major overhaul / unification of behavior lookups.
    """

    def __call__(self):
        from plone.behavior.interfaces import IBehaviorAssignable
        from plone.dexterity.schema import SCHEMA_CACHE

        def __getattr__(self, name):
            # python basics:  __getattr__ is only invoked if the attribute wasn't
            # found by __getattribute__
            #
            # optimization: sometimes we're asked for special attributes
            # such as __conform__ that we can disregard (because we
            # wouldn't be in here if the class had such an attribute
            # defined).
            # also handle special dynamic providedBy cache here.
            if name.startswith('__') or name == '_v__providedBy__':
                raise AttributeError(name)

            # attribute was not found; try to look it up in the schema and return
            # a default
            value = _default_from_schema(
                self,
                SCHEMA_CACHE.get(self.portal_type),
                name
            )
            if value is not _marker:
                return value

            # do the same for each subtype
            assignable = IBehaviorAssignable(self, None)
            if assignable is not None:
                for behavior_registration in assignable.enumerateBehaviors():
                    if behavior_registration.interface:
                        value = _default_from_schema(
                            self,
                            behavior_registration.interface,
                            name
                        )
                        if value is not _marker:
                            return value

            raise AttributeError(name)

        from plone.dexterity.content import DexterityContent
        from plone.dexterity.content import Item
        self.patch_refs(DexterityContent, '__getattr__', __getattr__)
        self.patch_refs(Item, '__getattr__', __getattr__)
