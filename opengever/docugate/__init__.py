from opengever.docugate.interfaces import IDocugateSettings
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.docugate')


def is_docugate_feature_enabled():
    office_connector_enabled = api.portal.get_registry_record(
        "direct_checkout_and_edit_enabled",
        interface=IOfficeConnectorSettings)
    docugate_enabled = api.portal.get_registry_record(
        'is_feature_enabled', interface=IDocugateSettings)
    return office_connector_enabled and docugate_enabled
