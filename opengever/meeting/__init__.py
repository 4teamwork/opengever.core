from functools import wraps
from opengever.meeting.exceptions import WordMeetingImplementationDisabledError
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
    """There is no longer a separate flag for word.
    """
    return is_meeting_feature_enabled()


def require_word_meeting_feature(func):
    """Decorator for making sure that a function or method is only called
    when the word meeting feature is enabled.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_word_meeting_implementation_enabled():
            raise WordMeetingImplementationDisabledError()
        return func(*args, **kwargs)
    return wrapper
