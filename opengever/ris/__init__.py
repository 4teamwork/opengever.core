from opengever.ris.interfaces import IRisSettings
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.ris")

LEGACY_PROPOSAL_TYPE = "opengever.meeting.proposal"


RIS_VIEW_STATE_CHANGE = 'spv/antrag-status-modifizieren'


def is_ris_feature_enabled():
    return bool(
        api.portal.get_registry_record(name='base_url', interface=IRisSettings)
    )
