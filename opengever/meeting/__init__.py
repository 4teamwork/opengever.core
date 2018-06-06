from opengever.meeting.interfaces import IMeetingSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.meeting')


def is_meeting_feature_enabled():
    try:
        registry = getUtility(IRegistry)
        return registry.forInterface(IMeetingSettings).is_feature_enabled

    except (KeyError, AttributeError):
        return False
