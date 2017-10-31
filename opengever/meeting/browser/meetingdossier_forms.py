from opengever.base.behaviors.utils import hide_fields_from_behavior
from opengever.dossier.browser.forms import DossierAddForm
from opengever.dossier.browser.forms import DossierAddView
from opengever.dossier.browser.forms import DossierEditForm


class MeetingDossierAddForm(DossierAddForm):

    def updateFields(self):
        super(MeetingDossierAddForm, self).updateFields()
        hide_fields_from_behavior(self, ['IOpenGeverBase.title'])


class MeetingDossierAddView(DossierAddView):

    form = MeetingDossierAddForm


class MeetingDossierEditForm(DossierEditForm):

    def updateFields(self):
        super(MeetingDossierEditForm, self).updateFields()
        hide_fields_from_behavior(self, ['IOpenGeverBase.title'])
