from opengever.disposition import _
from opengever.disposition.appraisal import IAppraisal
from plone import api
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


class AppraiseView(BrowserView):
    """View to do appraise transition.

    Checks if the appraisal is complete (selection for every dossier).
    """

    transition = 'disposition-transition-appraise'

    def __call__(self):
        if not IAppraisal(self.context).is_complete():
            msg = _(u'msg_appraisal_incomplete',
                    default=u'The appraisal is incomplete, appraisal could '
                    'not be finalized.')
            api.portal.show_message(
                message=msg, request=self.request, type='error')

            return self.request.RESPONSE.redirect(self.context.absolute_url())

        return self.request.RESPONSE.redirect(
            '{}/content_status_modify?workflow_action={}'.format(
                self.context.absolute_url(), self.transition))
