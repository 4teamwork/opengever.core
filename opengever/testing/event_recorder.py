from persistent.list import PersistentList
from zope.component.hooks import getSite


EVENT_RECORD_ATTRIBUTE_NAME = '_og_testing_events_record'
EVENT_RECORD_SERIALIZERS = {}
_marker = object()


def register_event_recorder(*required):
    """Register a generic event subscriber for recording certain events.

    In order to be able to use the testbrowser, the transaction must be able to
    synchronize the threads. The easiest way to do that is to store the infos
    in the database. We do that by just attaching them to the Plone site.
    """
    getSite().getSiteManager().registerHandler(
        recording_event_subscriber, list(required))


def get_recorded_events():
    """Return all recorded events as tuple of the event classname (string)
    """
    return getattr(getSite(), EVENT_RECORD_ATTRIBUTE_NAME, ())


def get_last_recorded_event():
    """Returns the tuple of the last recorded event.
    The tuple contains the string of the event class name and the serialized
    data of the event.
    """
    events = get_recorded_events()
    if events:
        return events[-1]
    else:
        return None


def recording_event_subscriber(*args):
    site = getSite()
    if not hasattr(site, EVENT_RECORD_ATTRIBUTE_NAME):
        events = PersistentList()
        setattr(site, EVENT_RECORD_ATTRIBUTE_NAME, events)
    else:
        events = getattr(site, EVENT_RECORD_ATTRIBUTE_NAME)

    if len(args) == 1:
        events.append(args[0])
    else:
        events.append(args)
