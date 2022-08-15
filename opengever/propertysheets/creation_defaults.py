from copy import copy
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.propertysheets.utils import get_customproperties_behavior
from zope.component import queryAdapter
from zope.schema import getFields


def initialize_customproperties_defaults(obj, reindex=True):
    behavior_iface = get_customproperties_behavior(obj)
    behavior = queryAdapter(obj, behavior_iface)
    if behavior:
        # Only attempt to set defaults if no actual custom properties exist yet
        if behavior.custom_properties:
            return

        custom_prop_defaults = get_customproperties_defaults(
            behavior_iface['custom_properties'])

        field = getFields(behavior_iface).get('custom_properties')
        active_slot = field.get_active_assignment_slot(obj)
        default_slot = field.default_slot

        defaults_to_store = {}
        if custom_prop_defaults.get(active_slot):
            defaults_to_store[active_slot] = custom_prop_defaults.get(active_slot)
        if custom_prop_defaults.get(default_slot):
            defaults_to_store[default_slot] = custom_prop_defaults.get(default_slot)
        if not defaults_to_store:
            return

        behavior.custom_properties = defaults_to_store
        if reindex:
            obj.reindexObject()


def get_customproperties_defaults(propsheet_field):
    """Returns defaults for all custom properties on a given PropertySheetField.

    These are *creation* defaults, intended to be used during or immediately
    after initial object creation. They therefore get determined on an unbound
    field, because no context (the object to be created) exists yet.

    Defaults are returned as a sparse representation in the PropertySheetField
    internal format (a {slot_name: {field_name: field_value}} mapping).

    For example:
    {u'IDocument.default': {u'language': u'en'}}
    """
    default_values_by_slot = {}

    storage = PropertySheetSchemaStorage()
    for slot_name in propsheet_field.valid_assignment_slots_factory():
        slot_values = {}
        definition = storage.query(slot_name)

        if definition is not None:
            for (field_name, field) in definition.get_fields():
                if field.default is not None:
                    # Make sure to dereference defaults that have possibly
                    # been declared as a mutable kwarg
                    default = copy(field.default)

                    slot_values[field.__name__] = default

            if slot_values:
                default_values_by_slot[slot_name] = slot_values

    return default_values_by_slot
