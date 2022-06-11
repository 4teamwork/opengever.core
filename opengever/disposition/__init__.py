from opengever.disposition.interfaces import IDispositionSettings
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.disposition')

def only_attach_original_enabled():
    """checks if the feature flag only_attach_original_if_conversion_is_missing
    is enabled"""

    return api.portal.get_registry_record(
        'only_attach_original_if_conversion_is_missing',
        interface=IDispositionSettings)
