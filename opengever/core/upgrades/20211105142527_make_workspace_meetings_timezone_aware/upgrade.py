from ftw.upgrade import UpgradeStep
from opengever.workspace.interfaces import IWorkspaceMeeting
from pytz import utc


class MakeWorkspaceMeetingsTimezoneAware(UpgradeStep):
    """Make workspace meetings timezone aware.
    """

    def __call__(self):
        query = {'object_provides': [IWorkspaceMeeting.__identifier__]}
        for obj in self.objects(query, 'Ensure workspace meeting start and '
                                'end are timezone aware'):
            self.localize_field(obj, "start")
            self.localize_field(obj, "end")
            # This is somewhat a hack. By reindexing the full object we change
            # the modified date, so that when checking whether the metadata has
            # changed, we never reach the comparison with previous value for
            # the start and end Fields, which would fail because we are
            # comparing timezone naive and aware datetimes.
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
