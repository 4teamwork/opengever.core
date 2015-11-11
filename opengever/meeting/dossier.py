from five import grok
from opengever.dossier.base import DossierContainer
from opengever.dossier.behaviors.dossier import AddForm
from opengever.meeting.model import Meeting


class MeetingDossier(DossierContainer):

    def get_meeting(self):
        return Meeting.query.by_dossier(self).first()


class MeetingDossierAddForm(AddForm):
    grok.name('opengever.meeting.meetingdossier')
