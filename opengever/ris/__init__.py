from opengever.ris.interfaces import IRisSettings
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.ris")

LEGACY_PROPOSAL_TYPE = "opengever.meeting.proposal"

RIS_VIEW_ADD_PROPOSAL = 'spv/antrag-erstellen'
RIS_VIEW_EDIT = 'spv/antrag-bearbeiten'
RIS_VIEW_TRANSITION_SUBMIT = 'spv/antrag-einreichen'
RIS_VIEW_TRANSITION_CANCEL = 'spv/antrag-stornieren'
RIS_VIEW_TRANSITION_REACTIVATE = 'spv/antrag-wiedereroeffnen'


def is_ris_feature_enabled():
    return bool(
        api.portal.get_registry_record(name='base_url', interface=IRisSettings)
    )
