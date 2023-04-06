from datetime import datetime
from opengever.document.behaviors import IBaseDocument
from opengever.propertysheets.definition import SolrDynamicField
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from zope.schema import getFields
from zope.schema._field import Date


def cast_custom_property_value(value, field):
    if isinstance(field, Date):
        if type(value) == datetime:
            return value.date()
    return value


def get_customproperties_behavior(obj):
    from opengever.document.behaviors.customproperties import IDocumentCustomProperties
    from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
    from opengever.dossier.behaviors.dossier import IDossierMarker
    if IDossierMarker.providedBy(obj):
        return IDossierCustomProperties
    elif IBaseDocument.providedBy(obj):
        return IDocumentCustomProperties

    return


def get_custom_properties(obj, docprops_only=False):
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
            if (docprops_only and name in definition.docprops) or not docprops_only:
                data[name] = custom_properties[slot].get(name)

    return data


def set_custom_property(obj, fieldname, value, reindex=False):
    customprops_behavior = get_customproperties_behavior(obj)
    adapted = customprops_behavior(obj, None)
    custom_props = adapted.custom_properties or {}

    field = getFields(customprops_behavior).get('custom_properties')
    active_slot = field.get_active_assignment_slot(obj)
    for slot in [active_slot, field.default_slot]:
        if slot is None:
            continue

        definition = PropertySheetSchemaStorage().query(slot)
        if not definition:
            continue

        for slot_fieldname, slot_field in definition.get_fields():
            if fieldname != slot_fieldname:
                continue

            if slot not in custom_props:
                custom_props[slot] = {}

            custom_props[slot][fieldname] = cast_custom_property_value(value, slot_field)

            field.set(field.interface(obj), custom_props)
            if reindex:
                solr_field = SolrDynamicField(
                    fieldname, definition.schema_class[fieldname])
                obj.reindexObject(idxs=["UID", solr_field.solr_field_name])
            return
