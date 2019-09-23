from ftw.upgrade import UpgradeStep
from opengever.base.touched import RECENTLY_TOUCHED_KEY
from tzlocal import get_localzone
from zope.annotation import IAnnotations


class MigrateDatesInRecentlyTouchedMenu(UpgradeStep):
    """Migrate dates in recently touched menu.
    """

    def __call__(self):
        local_tz = get_localzone()
        annotations = IAnnotations(self.portal)
        touched_store = annotations.get(RECENTLY_TOUCHED_KEY)
        if not touched_store:
            return

        for userid in touched_store.keys():
            for entry in touched_store[userid]:
                naive_touched_date = entry['last_touched']
                entry['last_touched'] = naive_touched_date.replace(tzinfo=local_tz)
