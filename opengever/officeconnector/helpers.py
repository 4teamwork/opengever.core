from plone import api
from opengever.officeconnector.interfaces import IOfficeConnectorSettings


def is_officeconnector_attach_feature_enabled():
    return api.portal.get_registry_record('attach_to_outlook_enabled',
                                          interface=IOfficeConnectorSettings)


def is_officeconnector_checkout_feature_enabled():
    return api.portal.get_registry_record('direct_checkout_and_edit_enabled',
                                          interface=IOfficeConnectorSettings)
