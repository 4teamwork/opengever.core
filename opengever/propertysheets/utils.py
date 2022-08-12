from opengever.document.behaviors import IBaseDocument
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from zope.schema import getFields


def get_customproperties_behavior(obj):
    from opengever.document.behaviors.customproperties import IDocumentCustomProperties
    from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
    from opengever.dossier.behaviors.dossier import IDossierMarker
    if IDossierMarker.providedBy(obj):
        return IDossierCustomProperties
    elif IBaseDocument.providedBy(obj):
        return IDocumentCustomProperties

    return


def get_custom_properties(obj):
    data = {}

    customprops_behavior = get_customproperties_behavior(obj)
    if customprops_behavior is None:
        return data

    adapted = customprops_behavior(obj, None)
    if not adapted:
        return data

    custom_properties = adapted.custom_properties
    if not custom_properties:
        return data

    field = getFields(customprops_behavior).get('custom_properties')
    active_slot = field.get_active_assignment_slot(obj)
    for slot in [active_slot, field.default_slot]:
        if slot not in custom_properties:
            continue

        definition = PropertySheetSchemaStorage().query(slot)
        if not definition:
            continue

        for name, field in definition.get_fields():
            data[name] = custom_properties[slot].get(name)

    return data
