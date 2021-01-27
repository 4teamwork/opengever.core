from opengever.propertysheets.storage import PropertySheetSchemaStorage


GROUPNAME = "custom_properties"


def omit_custom_properties_group(form_groups):
    """Omit form group `custom_properties` if no schemas are defined."""

    if not PropertySheetSchemaStorage():
        return [group for group in form_groups if group.__name__ != GROUPNAME]

    return form_groups
