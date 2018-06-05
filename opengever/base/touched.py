from BTrees.OOBTree import OOBTree
from datetime import datetime
from opengever.base.interfaces import IRecentlyTouchedSettings
from opengever.document.behaviors import IBaseDocument
from operator import itemgetter
from persistent.list import PersistentList
from plone import api
from plone.api.portal import get_registry_record
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implements
import logging


RECENTLY_TOUCHED_KEY = 'opengever.base.touched.recently_touched'
RECENTLY_TOUCHED_INTERFACES_TO_TRACK = [
    IBaseDocument,
]

logger = logging.getLogger('opengever.base.touched')


class IObjectTouchedEvent(IObjectEvent):
    """An object has been touched"""


class ObjectTouchedEvent(ObjectEvent):
    """An object has been touched"""

    implements(IObjectTouchedEvent)


def handle_object_touched(context, event):
    handler = ObjectTouchedHandler()
    handler.log_touched_object(context, event)


def should_track_touches(obj):
    """Return True if touches for this type should be tracked, False otherwise.
    """
    return any(iface.providedBy(obj)
               for iface in RECENTLY_TOUCHED_INTERFACES_TO_TRACK)


class ObjectTouchedHandler(object):
    """Handles logging of ObjectTouchedEvents.

    This class takes care of logging ObjectTouchedEvents, as well as keeping
    the logs sorted and rotated (truncated to the current limit).
    """

    def __init__(self):
        self.portal = api.portal.get()
        self.catalog = api.portal.get_tool('portal_catalog')

    def ensure_log_initialized(self, user_id):
        ann = IAnnotations(self.portal)
        if RECENTLY_TOUCHED_KEY not in ann:
            ann[RECENTLY_TOUCHED_KEY] = OOBTree()

        if user_id not in ann[RECENTLY_TOUCHED_KEY]:
            ann[RECENTLY_TOUCHED_KEY][user_id] = PersistentList()

    def log_touched_object(self, context, event):
        # Only log touches for tracked types
        if not should_track_touches(context):
            return

        logger.info("Object touched: %r (UID: %s)" % (context, IUUID(context)))
        current_user_id = api.user.get_current().id

        self.ensure_log_initialized(current_user_id)
        recently_touched_log = self.get_recently_touched_log(current_user_id)

        # Deduplicate - only keep the most recent entry for any object.
        # (Which is the one we're about to add)
        obj_uid = IUUID(context)
        for entry in recently_touched_log:
            if entry['uid'] == obj_uid:
                recently_touched_log.remove(entry)

        # Store touched items in order - most recent first
        recently_touched_log.insert(
            0, {'last_touched': datetime.now(), 'uid': obj_uid})

        self.sort(recently_touched_log)
        self.rotate(current_user_id)

    def get_recently_touched_log(self, user_id):
        return IAnnotations(self.portal)[RECENTLY_TOUCHED_KEY][user_id]

    def sort(self, recently_touched_log):
        """Sort entire list on write - this way, eventual errors self-correct.

        This leads to a minor performance penalty on write, but:
        Sorting an already *mostly* sorted sequence is substantially cheaper
        than having to sort an entirely unordered sequence, especially with
        Python's Timsort. Therefore, the penalty should be minimal.
        """
        recently_touched_log.sort(key=itemgetter('last_touched'), reverse=True)

    def rotate(self, user_id):
        """Rotate recently touched log.

        We basically truncate it to the RECENTLY_TOUCHED_LIMIT.

        However, because the display limit only applies to recently touched
        items (not checked out docs), we need to take care to calculate the
        correct cutoff by "ignoring" checked out docs (adding them to the
        cutoff limit).
        """
        num_checked_out = len(self.catalog(checked_out=user_id))
        limit = get_registry_record('limit', IRecentlyTouchedSettings)
        cutoff = limit + num_checked_out
        truncated = self.get_recently_touched_log(user_id)[:cutoff]
        IAnnotations(self.portal)[RECENTLY_TOUCHED_KEY][user_id] = truncated
