from opengever.base.formutils import hide_field_by_name
from opengever.dossier.browser.forms import DossierAddForm
from opengever.dossier.browser.forms import DossierAddView
from opengever.dossier.browser.forms import DossierEditForm


class MeetingDossierAddForm(DossierAddForm):

    def updateFields(self):
        super(MeetingDossierAddForm, self).updateFields()
        hide_field_by_name(self, 'IOpenGeverBase.title')


class MeetingDossierAddView(DossierAddView):

    form = MeetingDossierAddForm


class MeetingDossierEditForm(DossierEditForm):

    def updateFields(self):
        super(MeetingDossierEditForm, self).updateFields()
        hide_field_by_name(self, 'IOpenGeverBase.title')
