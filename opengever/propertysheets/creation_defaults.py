from copy import copy
from opengever.document.behaviors import IBaseDocument
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from zope.component import queryAdapter


def get_customproperties_behavior(obj):
    # Avoid import problems when importing a bundle
    from opengever.document.behaviors.customproperties import IDocumentCustomProperties
    from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
    from opengever.dossier.behaviors.dossier import IDossierMarker

    if IDossierMarker.providedBy(obj):
        return IDossierCustomProperties
    elif IBaseDocument.providedBy(obj):
        return IDocumentCustomProperties

    return


def initialize_customproperties_defaults(obj, reindex=True):
    behavior_iface = get_customproperties_behavior(obj)
    behavior = queryAdapter(obj, behavior_iface)
    if behavior:
        custom_prop_defaults = get_customproperties_defaults(
            behavior_iface['custom_properties'])

        if not custom_prop_defaults:
            return

        # Only attempt to set defaults if no actual custom properties exist yet
        if not behavior.custom_properties:
            behavior.custom_properties = custom_prop_defaults
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
