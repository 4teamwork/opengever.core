from opengever.dossier.base import DossierContainer
from opengever.meeting.model import Meeting


class MeetingDossier(DossierContainer):

    def get_meeting(self):
        return Meeting.query.by_dossier(self).first()
