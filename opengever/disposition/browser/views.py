from five import grok
from opengever.disposition.appraisal import IAppraisal
from zope.interface import Interface
import json


class UpdateAppraisalView(grok.View):
    """View to update a the appraisal for a specific dossier.

    Used by the DispositionOverview via AJAX request.
    """
    grok.context(Interface)
    grok.name('update_appraisal_view')
    grok.require('zope2.View')

    def render(self):
        IAppraisal(self.context).update(
            intid=json.loads(self.request['dossier-id']),
            archive=json.loads(self.request['appraisal']))
