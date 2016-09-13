from opengever.officeatwork.interfaces import IOfficeatworkSettings
from plone import api


def is_officeatwork_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IOfficeatworkSettings)
