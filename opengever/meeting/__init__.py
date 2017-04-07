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


def is_word_meeting_implementation_enabled():
    """The word implementation is a new implementation of parts of the meeting
    feature.
    It allows to do much more directly in Word instead of using structured
    fields in GEVER.

    This is a feature flag so that we can develop the new version in parallel
    and switch it in production at a later point.
    The feature flag only works when the base meeting feature is enabled.

    Switching from old to new by activating this flag should only happen when
    there are no meeting objects, since they are currently not migrated
    automatically.
    """
    if not is_meeting_feature_enabled():
        return False

    try:
        registry = getUtility(IRegistry)
        return (registry.forInterface(IMeetingSettings)
                .is_word_implementation_enabled)

    except (KeyError, AttributeError):
        return False
