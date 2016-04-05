from opengever.bumblebee.interfaces import IGeverBumblebeeSettings
from plone import api


def is_bumblebee_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IGeverBumblebeeSettings)
