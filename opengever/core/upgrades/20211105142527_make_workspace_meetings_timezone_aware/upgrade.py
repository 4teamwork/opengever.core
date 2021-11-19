from ftw.upgrade import UpgradeStep
from opengever.workspace.interfaces import IWorkspaceMeeting
from pytz import utc


class MakeWorkspaceMeetingsTimezoneAware(UpgradeStep):
    """Make workspace meetings timezone aware.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': [IWorkspaceMeeting.__identifier__]}
        to_reindex = []
        for obj in self.objects(query, 'Ensure workspace meeting start and '
                                'end are timezone aware'):
            self.localize_field(obj, "start")
            self.localize_field(obj, "end")
            # Simply reindexing might fail, as it can lead to comparing
            # timezone aware and timezone naive datetimes when determining
            # whether an update of the metadata is necessary. Instead we
            # we first unindex the objects, then make sure to process the
            # indexing queue, before reindexing them.
            to_reindex.append(obj)
            obj.unindexObject()

        # make a catalog query to make sure to process the indexing queue
        self.catalog_unrestricted_search(query)
        for obj in to_reindex:
            obj.reindexObject()

    def localize_field(self, obj, fieldname):
        value = getattr(obj, fieldname)
        if not value:
            return
        if value.tzinfo is not None:
            value = value.astimezone(utc)
        else:
            value = utc.localize(value)
        setattr(obj, fieldname, value)
