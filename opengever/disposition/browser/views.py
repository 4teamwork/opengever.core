from opengever.disposition.appraisal import IAppraisal
from Products.Five.browser import BrowserView
import json


class UpdateAppraisalView(BrowserView):
    """View to update a the appraisal for a specific dossier.

    Used by the DispositionOverview via AJAX request.
    """

    def __call__(self):
        IAppraisal(self.context).update(
            intid=json.loads(self.request['dossier-id']),
            archive=json.loads(self.request['should_be_archived']))
