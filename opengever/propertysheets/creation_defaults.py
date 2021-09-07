from opengever.propertysheets.storage import PropertySheetSchemaStorage
from zope.component import queryAdapter


def initialize_customproperties_defaults(obj, behavior_iface):
    behavior = queryAdapter(obj, behavior_iface)
    if behavior:
        custom_prop_defaults = get_customproperties_defaults(
            behavior_iface['custom_properties'])

        # Only attempt to set defaults if no actual custom properties exist yet
        if not behavior.custom_properties:
            behavior.custom_properties = custom_prop_defaults
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
                    slot_values[field.__name__] = field.default

            if slot_values:
                default_values_by_slot[slot_name] = slot_values

    return default_values_by_slot
