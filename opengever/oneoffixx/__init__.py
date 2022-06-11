from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.oneoffixx.interfaces import IOneoffixxSettings
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.oneoffixx")


def is_oneoffixx_feature_enabled():
    office_connector_enabled = api.portal.get_registry_record(
        "direct_checkout_and_edit_enabled",
        interface=IOfficeConnectorSettings)
    oneoffixx_enabled = api.portal.get_registry_record(
        'is_feature_enabled', interface=IOneoffixxSettings)
    return office_connector_enabled and oneoffixx_enabled
