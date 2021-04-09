from ftw.upgrade import UpgradeStep
from opengever.workspace.interfaces import IWorkspaceMeeting


class IndexAttendeesInSolr(UpgradeStep):
    """Index attendees in solr.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'object_provides': IWorkspaceMeeting.__identifier__}
        for meeting in self.objects(query, 'Reindex meeting attendees'):
            meeting.reindexObject(idxs=['UID', 'attendees'])
