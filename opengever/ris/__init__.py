from opengever.ris.interfaces import IRisSettings
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.ris")


def is_ris_feature_enabled():
    return bool(
        api.portal.get_registry_record(name='base_url', interface=IRisSettings)
    )
