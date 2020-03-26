from opengever.wopi.interfaces import IWOPISettings
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.wopi')


def is_wopi_feature_enabled():
    enabled = api.portal.get_registry_record(
            name='enabled', interface=IWOPISettings)
    discovery_url = api.portal.get_registry_record(
            name='discovery_url', interface=IWOPISettings)
    return bool(enabled and discovery_url)
