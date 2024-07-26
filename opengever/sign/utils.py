from opengever.sign.interfaces import ISignSettings
from plone import api


def is_sign_feature_enabled():
    return api.portal.get_registry_record('is_feature_enabled', interface=ISignSettings)
