from five import grok
from opengever.dossier.base import DossierContainer
from opengever.dossier.behaviors.dossier import AddForm


class MeetingDossier(DossierContainer):
    pass


class MeetingDossierAddForm(AddForm):
    grok.name('opengever.meeting.meetingdossier')
