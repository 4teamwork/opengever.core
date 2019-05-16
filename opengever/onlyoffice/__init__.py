from plone import api
from opengever.onlyoffice.interfaces import IOnlyOfficeSettings


def is_onlyoffice_feature_enabled():
    enabled = api.portal.get_registry_record(
            name='enabled', interface=IOnlyOfficeSettings)
    api_url = api.portal.get_registry_record(
            name='documentserver_api_url', interface=IOnlyOfficeSettings)
    return bool(enabled and api_url)
