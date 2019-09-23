from ftw.upgrade import UpgradeStep
from opengever.base.touched import RECENTLY_TOUCHED_KEY
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from tzlocal import get_localzone
from zope.annotation import IAnnotations


class MigrateDatesInRecentlyTouchedMenu(UpgradeStep):
    """Migrate dates in recently touched menu. Additional to the date
    migration we switch to PersistentMapping instead of simple dicts.
    """

    def __call__(self):
        local_tz = get_localzone()
        annotations = IAnnotations(self.portal)
        touched_store = annotations.get(RECENTLY_TOUCHED_KEY)
        if not touched_store:
            return

        for userid in touched_store.keys():
            temp_entry_list = PersistentList()
            for entry in touched_store[userid]:
                naive_touched_date = entry['last_touched']
                entry['last_touched'] = naive_touched_date.replace(tzinfo=local_tz)

                # Replace the list with a copy of the list but
                # using persistent mappings.
                temp_entry_list.append(PersistentMapping(entry))

            touched_store[userid] = temp_entry_list
