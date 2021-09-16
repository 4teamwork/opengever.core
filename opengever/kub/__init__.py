from opengever.kub.interfaces import IKuBSettings
from plone import api


def is_kub_feature_enabled():
    return bool(
        api.portal.get_registry_record(
            name='base_url', interface=IKuBSettings))
