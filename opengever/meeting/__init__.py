from opengever.meeting.interfaces import IMeetingSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.meeting')


def is_meeting_feature_enabled():
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IMeetingSettings)
    return settings.is_feature_enabled
