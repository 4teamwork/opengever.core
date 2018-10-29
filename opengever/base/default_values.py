"""
This module contains functions to help fix issues around Dexterity's
behavior regarding default values.

Default values not being persisted
----------------------------------

In some cases, default values that have been prefilled in a z3c.form form won't
get persisted in the DB, causing an object's fields to "retroactively change"
once the default[Factory] for a field is changed.

Both these cases share a similar pattern: z3c.form checks whether a field's
value has changed or not, and only writes fields whose values it believes
have changed. However, that check gets fooled by __getattr__ fallbacks in
DexterityContent and AnnotationsFactoryImpl that don't raise AttributeError,
but return the field's default or missing_value respectively.

1) - AttributeStorage

Given:

- Field in base schema or a behavior using AttributeStorage
- Field has a default or a defaultFactory

Steps to reproduce:

- Add a new object using the z3c.form add form, leaving the field at its
  prefilled default value (Add & immediately save)
- Change the field's default or defaultFactory in the code

=> The field's value will not have been persisted.

(When displaying the field or reading it programmatically, the new default
will be returned, indicating that the old default has never been persisted.)

This happens because z3c.form checks whether a field has been changed or not
when applying changes, and only saves values that are different
(see z3c.form.form.applyChanges()).

Because plone.dexterity's DexterityContent defines a __getattr__ that falls
back to a field's default instead of raising an AttributeError, for a newly
created object, accessing an attribute that doesn't exist yet will result in
the fields default value.

This will lead z3c.form to comparing the field's default value (prefilled in
the form's widget) with the field's default value (returned by Dexterity's
fallback when accessing a non-existent attribute). Because of that the field's
value is never considered "changed", and therefore won't be written to the
object.

On the surface things appear to have worked though, because Dexterity's
fallback also will dynamically return the default on display / programmatic
read access.

2) - AnnotationStorage

Given:

- Field in a behavior using AnnotationStorage
- Field default that is equal to field's missing_value

Steps to reproduce:

- Add a new object using the z3c.form add form, leaving the field at its
  prefilled default value (Add & immediately save)
- Change the field's default or defaultFactory in the code

=> The field's value will not have been persisted.

In this case, the value isn't being persisted because there is a similar
fallback in AnnotationsFactoryImpl: Instead of raising an AttributeError, it
will fall back to returning the field's missing_value
(see plone.behavior.annotation.AnnotationsFactoryImpl.__getattr__).

This will result in z3c.form.form.applyChanges() comparing the default value
for a field against the field's missing_value - if they happen to be the same,
the field's value will never be persisted.

Approach to fixing the issues
-----------------------------

We attempt to fix the z3c.form related issues where default values won't be
persisted by patching z3c.form.util.changedField(). The idea is to patch it in
a way so that it doesn't just rely on the DataManager to return a field's
value (which would trigger the mentioned fallbacks), but instead uses the
function below to really get to the persisted value for a field, taking the
underlying storage into account. That way we can hopefully avoid any fallbacks
that would fool the check.
"""

from Acquisition import aq_base
from persistent.interfaces import IPersistent
from plone.app.dexterity.behaviors import metadata
from plone.behavior.annotation import AnnotationsFactoryImpl
from plone.dexterity.utils import iterSchemata
from plone.dexterity.utils import iterSchemataForType
from zope.schema import getFieldsInOrder
from zope.schema._bootstrapinterfaces import IContextAwareDefaultFactory


NO_DEFAULT_MARKER = object()


def get_persisted_value_for_field(context, field):
    """Return the *real* stored value for a field, avoiding any fallbacks.

    In particular, this circumvents the __getattr__ fallbacks in
    DexterityContent and AnnotationsFactoryImpl that return the field's
    default / missing_value.

    Raises an AttributeError if there is no stored value for the field.

    What we need to do here is basically to decide whether the storage
    implementation used for the given field on this context has any
    fallbacks (to default or missing value) in place. If it does, we need to
    bypass them and only return the actually persisted value, or raise an
    AttributeError.

    We also deal with fields that are implemented as properties (which are
    to be found in the class dict instead of the instance dict).
    """
    name = field.getName()
    if not IPersistent.providedBy(context):
        raise Exception(
            "Attempt to get persisted field value for a non-persistent object "
            "for field %r on obj %r" % (name, context))

    # AQ unwrap object to avoid finding an attribute via acquisition
    context = aq_base(context)
    storage_impl = field.interface(context)

    def classname(obj):
        """Stringy alternative to instance checks to avoid circular imports.
        """
        return getattr(getattr(obj, '__class__', object), '__name__', '')

    if isinstance(storage_impl, AnnotationsFactoryImpl):
        # AnnotationStorage
        if name not in storage_impl.__dict__['schema']:
            raise AttributeError(name)

        annotations = storage_impl.__dict__['annotations']
        key_name = storage_impl.__dict__['prefix'] + name
        try:
            value = annotations[key_name]
        except KeyError:
            # Don't do the fallback to field.missing_value that
            # AnnotationsFactoryImpl.__getattr__ does
            raise AttributeError(name)
        return value
    elif storage_impl is context:
        # Assume attribute storage
        try:
            # Two possible cases here: Field in base schema, or field in
            # behavior with attribute storage. Either way, we look up the
            # attribute in the object's __dict__ in order to circumvent the
            # fallback in DexterityContent.__getattr__
            value = storage_impl.__dict__[name]
        except KeyError:
            # Check whether the field is a property
            descriptor = storage_impl.__class__.__dict__.get(name)
            if isinstance(descriptor, property):
                # Invoke the property's getter
                return descriptor.fget(storage_impl)
            raise AttributeError(name)
        return value
    elif classname(storage_impl) in ('TranslatedTitle', 'OGMailBase', 'Changed'):
        # These factories wrap a context that inherits from DexterityContent,
        # accessed via storage_impl.context.
        # So we need to apply the same strategy as for direct attribute
        # storage to accessing attributes on that context in order to bypass
        # the __getattr__ fallback.
        try:
            value = storage_impl.context.__dict__[name]
        except KeyError:
            # Check whether the field is a property
            descriptor = storage_impl.__class__.__dict__.get(name)
            if isinstance(descriptor, property):
                # Invoke the property's getter
                return descriptor.fget(storage_impl)
            raise AttributeError(name)
        return value
    elif classname(storage_impl) == 'Versionable':
        # Versionable.changeNote is a property that isn't persisted, but
        # written to request annotations instead
        raise AttributeError(field.getName())
    elif isinstance(storage_impl, metadata.MetadataBase):
        # MetadataBase has its own default value fallback - bypass it
        try:
            value = context.__dict__[name]
        except KeyError:
            raise AttributeError
        return value
    else:
        # Unknown storage - bail
        raise Exception(
            "Unknown storage %r for field %r" % (storage_impl, name))


def get_persisted_values_for_obj(context):
    values = {}
    schemas = list(iterSchemata(context))
    for schema in schemas:
        fields = getFieldsInOrder(schema)
        for name, field in fields:
            try:
                value = get_persisted_value_for_field(context, field)
                values[name] = value
            except AttributeError:
                continue
    return values


def is_aq_wrapped(obj):
    try:
        obj.aq_base
        return True
    except AttributeError:
        return False


def object_has_value_for_field(obj, field):
    """Determine whether a value is persisted on `obj` for `field`.
    """
    try:
        get_persisted_value_for_field(obj, field)
        return True
    except AttributeError:
        return False


def determine_default_value(field, container):
    """Determine a field's default value during object creation.
    """
    # We deliberately ignore form level defaults here.

    # zope.schema defaultFactory
    #
    # Based on zope.schema._boostrapfields.DefaultProperty. We don't use
    # the class level 'default' attribute, which is a DefaultProperty,
    # because we want to be able to distinguish "default of None" and
    # "no default", at least for the defaultFactory. That's why it's
    # necessary to check in the instance dict for a defaultFactory first,
    # instead of letting the DefaultProperty implementation handle it.

    default_factory = field.__dict__.get('defaultFactory')
    if default_factory is not None:

        if IContextAwareDefaultFactory.providedBy(default_factory):
            # Access DefaultProperty descriptor to trigger validation
            field.bind(container).default
            return default_factory(container)
        else:
            # Access DefaultProperty descriptor to trigger validation
            field.default
            return default_factory()

    field_default = field.__dict__.get('default')
    if field_default is not None:
        # Access DefaultProperty descriptor to trigger validation
        field.default
        return field_default

    return NO_DEFAULT_MARKER


def set_default_values(content, container, values):
    """Set default values for all fields.

    (If no default value is available, fall back to setting missing value.)

    This is necessary for content created programmatically since dexterity
    doesn't persistenly set default values (or missing values) when creating
    content programmatically.

    Parameters:
    - content:   The object in creation. Might not be AQ wrapped yet
    - container: The parent container the object will be added to
    - values:    Mapping of *actual* values (not defaults) that will be or
                 have been set on the object (not by us). I.e. kwargs to
                 invokeFactory or createContentInContainer. Will be taken
                 into consideration when determining whether defaults should
                 apply or not.
    """
    # Canonicalize field names to short form (no prefix)
    fields_with_value = [k.split('.')[-1] for k in values.keys()]

    for schema in iterSchemata(content):
        for name, field in getFieldsInOrder(schema):

            if field.readonly:
                continue

            if name in fields_with_value:
                # Only set default if no *actual* value was supplied as
                # an argument to object construction
                continue

            if object_has_value_for_field(content, field):
                # Only set default if a value hasn't been set on the
                # object yet
                continue

            if not is_aq_wrapped(content):
                # Content isn't AQ wrapped - temporarily wrap it
                content = content.__of__(container)

            # Attempt to find a default value for the field
            value = determine_default_value(field, container)
            if value is NO_DEFAULT_MARKER:
                # No default found, fall back to missing value
                value = field.missing_value

            field.set(field.interface(content), value)


def inject_title_and_description_defaults(kw, portal_type, container):
    """If 'title' or 'description' fields have defaults, inject them into `kw`.

    These fields need special handling because they get set to an empty string
    in a hardcoded fashion in the P.CMFCore.PortalFolder.PortalFolderBase
    constructor if no *actual* value has been provided for them.

    This will later fool our set_default_values() because it thinks a
    legitimate value for these fields has already been persisted on the object,
    and will therefore not attempt to determine and set defaults for those
    fields.

    We therefore handle title and description differently by determining their
    defaults ahead of object construction time, and inject them into `kw` (
    unless *actual* values are already provided in `kw` of course).
    """
    to_check = ['title', 'description']

    # Don't do anything for fields that have an *actual* value provided
    for field_name in kw:
        if field_name in to_check:
            to_check.remove(field_name)

    schemas = iterSchemataForType(portal_type)
    for schema in schemas:
        for name, field in getFieldsInOrder(schema):
            # Return early if no more fields are left to check. No need to
            # iterate over dozens of irrelevant fields.
            if not to_check:
                return

            for fn_to_check in to_check:
                if fn_to_check == name:
                    dv = determine_default_value(field, container)
                    # If there is a default, and there is no *actual* value
                    # in `kw` that should be set, inject the default into `kw`
                    if dv is not NO_DEFAULT_MARKER:
                        kw[fn_to_check] = dv
                        to_check.remove(name)
