from ftw.upgrade import UpgradeStep
from opengever.workspace.interfaces import IWorkspaceMeeting


class ReindexMeetingParticipations(UpgradeStep):
    """Reindex meeting participations.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'object_provides': IWorkspaceMeeting.__identifier__}
        for meeting in self.objects(query, 'Reindex meeting participations'):
            meeting.reindexObject(idxs=['participations'])
