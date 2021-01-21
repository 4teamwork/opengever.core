GROUPNAME = "custom_properties"


def omit_custom_properties_group(form_groups):
    """Filter out the form group `custom_properties`.

    XXX Temporary workaround so we can move forward with custom properties in
    API `@schema` endpoint without proper classic UI support.
    """
    return [group for group in form_groups if group.__name__ != GROUPNAME]
