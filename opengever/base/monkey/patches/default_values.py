from copy import deepcopy
from opengever.base.interfaces import IDuringContentCreation
from opengever.base.monkey.patching import MonkeyPatch
from plone.dexterity.content import _marker
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
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
    from behavior schemas with *marker* interfaces.

    Rationale: The implementation in plone.dexterity 2.1.x grabs
    *marker interfaces* from SCHEMA_CACHE.subtypes() for behaviors that have
    them, instead of their schema interfaces.

    If there's a fallback logic in place (and we can't get rid of
    it), it should at least work consistently.

    The __getattr__ below is an exact copy of DexterityContent.__getattr__
    from plone.dexterity == 2.3.0. That version doesn't use SCHEMA_CACHE at
    all for behavior schemata, and so avoids using the questionable
    SCHEMA_CACHE.subtypes(). This was fixed in PR 21 in plone/plone.dexterity
    as part of a major overhaul / unification of behavior lookups.
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


class PatchDXCreateContentInContainer(MonkeyPatch):
    """Monkey patch Dexterity's createContentInContainer so that it sets
    default values for fields that haven't had a value passed in to the
    constructor.

    Additionaly, have the request provide IDuringContentCreation while content
    creation is in progress.
    """

    def __call__(self):
        from opengever.base.default_values import inject_title_and_description_defaults  # noqa
        from opengever.base.default_values import set_default_values
        from plone.dexterity.interfaces import IDexterityFTI
        from plone.dexterity.utils import addContentToContainer
        from zope.component import createObject
        from zope.component import getUtility
        from zope.event import notify
        from zope.lifecycleevent import ObjectCreatedEvent

        def createContentWithDefaults(portal_type, container, **kw):
            fti = getUtility(IDexterityFTI, name=portal_type)

            # Consider possible default values for title and description,
            # and inject them into kw if necessary.
            inject_title_and_description_defaults(kw, portal_type, container)

            content = createObject(fti.factory)
            set_default_values(content, container, kw)

            # Note: The factory may have done this already, but we want to be sure
            # that the created type has the right portal type. It is possible
            # to re-define a type through the web that uses the factory from an
            # existing type, but wants a unique portal_type!
            content.portal_type = fti.getId()

            for (key, value) in kw.items():
                setattr(content, key, value)

            notify(ObjectCreatedEvent(content))
            return content

        def createContentInContainer(container, portal_type, checkConstraints=True, **kw):
            alsoProvides(container.REQUEST, IDuringContentCreation)
            # Also pass container to createContent so it is available for
            # determining default values
            content = createContentWithDefaults(portal_type, container, **kw)
            result = addContentToContainer(
                container, content, checkConstraints=checkConstraints)
            noLongerProvides(container.REQUEST, IDuringContentCreation)
            return result

        from plone.dexterity import utils
        self.patch_refs(
            utils, 'createContentInContainer', createContentInContainer)


class PatchInvokeFactory(MonkeyPatch):
    """Monkey patch invokeFactory so that it sets default values for fields
    that haven't had a value passed in to the constructor.

    Additionaly, have the request provide IDuringContentCreation while content
    creation is in progress.
    """

    def __call__(self):
        from opengever.base.default_values import inject_title_and_description_defaults  # noqa
        from opengever.base.default_values import set_default_values
        from Products.CMFCore.utils import getToolByName

        def invokeFactory(self, type_name, id, RESPONSE=None, *args, **kw):
            """ Invokes the portal_types tool.
            """
            alsoProvides(self.REQUEST, IDuringContentCreation)
            pt = getToolByName(self, 'portal_types')
            myType = pt.getTypeInfo(self)

            if myType is not None:
                if not myType.allowType( type_name ):
                    raise ValueError('Disallowed subobject type: %s' % type_name)

            # Consider possible default values for title and description,
            # and inject them into kw if necessary.
            inject_title_and_description_defaults(kw, type_name, self)

            new_id = pt.constructContent(type_name, self, id, RESPONSE, *args, **kw)
            content = self[new_id]

            # Set default values
            set_default_values(content, self, kw)

            noLongerProvides(self.REQUEST, IDuringContentCreation)
            return new_id

        from Products.CMFCore.PortalFolder import PortalFolderBase
        self.patch_refs(PortalFolderBase, 'invokeFactory', invokeFactory)


class PatchZ3CFormChangedField(MonkeyPatch):
    """Patch changedField() so that it doesn't simply rely on the DataManager
    to return a field's stored value (which triggers fallbacks to the field's
    default / missing_value), but uses our helper function to access the real
    stored value, taking the underlying storage into account.
    """

    def __call__(self):
        from Acquisition import aq_base
        from Acquisition import ImplicitAcquisitionWrapper
        from opengever.base.default_values import get_persisted_value_for_field
        from persistent.interfaces import IPersistent
        from z3c.form import interfaces
        from z3c.formwidget.query.widget import QueryContext
        import zope.schema

        def changedField(field, value, context=None):
            """Figure if a field's value changed

            Comparing the value of the context attribute and the given value"""
            if context is None:
                context = field.context
            if context is None:
                # IObjectWidget madness
                return True
            if zope.schema.interfaces.IObject.providedBy(field):
                return True

            if not IPersistent.providedBy(context):
                # Field is not persisted, delegate to original implementation
                # Could be a z3c.formwidget QueryContex or an AQ wrapped dict
                # instance from Plone's TTW registry editor.
                assert any((
                    isinstance(context, QueryContext),
                    isinstance(context, ImplicitAcquisitionWrapper) and
                    isinstance(aq_base(context), dict),
                ))
                return original_changedField(field, value, context)

            dm = zope.component.getMultiAdapter(
                (context, field), interfaces.IDataManager)

            if not dm.canAccess():
                # Can't get the original value, assume it changed
                return True

            # Determine the original value
            # Use a helper method that actually returns the persisted value,
            # *without* triggering any fallbacks to default values or
            # missing values.
            try:
                stored_value = get_persisted_value_for_field(context, field)
            except AttributeError:
                return True

            if stored_value != value:
                return True

            return False

        from z3c.form import util
        locals()['__patch_refs__'] = False
        original_changedField = util.changedField
        self.patch_refs(util, 'changedField', changedField)


class PatchDexterityDefaultAddForm(MonkeyPatch):
    """Patch DefaultAddForm:

    - Patch update() to have the request provide IDuringContentCreation
      while content creation is in progress.
    - Patch create() to make sure default values are set when creating content
      via z3c.form add forms. This affects:
      - Fields where the current user lacks write permission
      - Fields omitted from the form
      - Fields whose widgets are in DISPLAY_MODE even in AddForms
    """

    def __call__(self):
        from Acquisition import aq_inner
        from opengever.base.default_values import set_default_values

        def update(self):
            alsoProvides(self.request, IDuringContentCreation)
            return original_update(self)

        def create(self, data):
            container = aq_inner(self.context)
            obj = original_create(self, data)
            set_default_values(obj, container, data)
            return obj

        from plone.dexterity.browser.add import DefaultAddForm
        locals()['__patch_refs__'] = False

        original_update = DefaultAddForm.update
        self.patch_refs(DefaultAddForm, 'update', update)

        original_create = DefaultAddForm.create
        self.patch_refs(DefaultAddForm, 'create', create)


class PatchBuilderCreate(MonkeyPatch):
    """Patch ftw.builder's create() so that it provides IDuringContentCreation
    while content creation is in progress.

    This is necessary for context aware defaultFactories to correctly
    determine whether the context they got passed is the object itself (edit)
    or the container (add).
    """

    def __call__(self):

        def create(*args, **kwargs):
            request = getRequest()
            if request is not None:
                alsoProvides(request, IDuringContentCreation)

            result = original_create(*args, **kwargs)

            request = getRequest()
            if request is not None:
                noLongerProvides(request, IDuringContentCreation)

            return result

        import ftw.builder
        original_create = ftw.builder.create
        locals()['__patch_refs__'] = False
        self.patch_refs(ftw.builder, 'create', create)


class PatchTransmogrifyDXSchemaUpdater(MonkeyPatch):
    """Patch transmogrify.dexterity's schema updater so it correctly
    sets default values, using our own `determine_default_value` function to
    determine the default, and `get_persisted_value_for_field` to avoid any
    __getattr__ fallbacks.
    """

    def __call__(self):
        from opengever.base import default_values
        from opengever.base.default_values import get_persisted_value_for_field
        from opengever.base.default_values import NO_DEFAULT_MARKER
        from transmogrify.dexterity.schemaupdater import _marker as _tm_marker
        from z3c.form.interfaces import NO_VALUE

        def determine_default_value(self, obj, field):
            """Determine the default to be set for a field that didn't receive
            a value from the pipeline.
            """
            default = default_values.determine_default_value(
                field, obj.aq_parent)
            if default is NO_DEFAULT_MARKER:
                default = field.default

            return default

        def update_field(self, obj, field, item):
            if field.readonly:
                return

            name = field.getName()
            value = self.get_value_from_pipeline(field, item)
            if value is not _tm_marker:
                field.set(field.interface(obj), value)
                return

            # Get the field's current value, if it has one then leave it alone
            try:
                value = get_persisted_value_for_field(obj, field)
            except AttributeError:
                value = NO_VALUE

            # Fix default description to be an empty unicode instead of
            # an empty bytestring because of this bug:
            # https://github.com/plone/plone.dexterity/pull/33
            if name == 'description' and value == '':
                field.set(field.interface(obj), u'')
                return

            if not(value is field.missing_value or value is NO_VALUE):
                return

            # Finally, set a default value if nothing is set so far
            default = self.determine_default_value(obj, field)
            field.set(field.interface(obj), default)

        from transmogrify.dexterity.schemaupdater import DexterityUpdateSection
        self.patch_refs(
            DexterityUpdateSection, 'determine_default_value',
            determine_default_value)
        self.patch_refs(
            DexterityUpdateSection, 'update_field',
            update_field)
