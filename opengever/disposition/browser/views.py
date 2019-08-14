from opengever.base.json_response import JSONResponse
from opengever.disposition import _
from opengever.disposition.appraisal import IAppraisal
from opengever.disposition.disposition import IDisposition
from plone import api
from Products.Five.browser import BrowserView
import json


class UpdateAppraisalView(BrowserView):
    """View to update a the appraisal for a specific dossier.

    Used by the DispositionOverview via AJAX request.
    """

    def __call__(self):
        appraisal = IAppraisal(self.context)
        should_be_archived = json.loads(self.request['should_be_archived'])
        if self.request.get('dossier-ids'):
            for intid in json.loads(self.request['dossier-ids']):
                appraisal.update(intid=intid, archive=should_be_archived)

        else:
            appraisal.update(
                intid=json.loads(self.request['dossier-id']),
                archive=should_be_archived)


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


class UpdateTransferNumberView(BrowserView):

    def __call__(self):
        transfer_number = self.request.form['transfer_number']
        IDisposition(self.context).transfer_number = transfer_number
        return JSONResponse(self.request).proceed().dump()


class GuardsView(BrowserView):
    """Provides some helper methods used by disposition workflow
    transition guards.
    """

    def is_appraised_to_closed_transition_available(self):
        """Returns only true when all dossiers has a negative appraisal.
        """
        return not self.context.has_dossiers_to_archive()

    def is_dispose_transition_available(self):
        """Returns only true when the disposition object contains dossiers
        with a positive appraisal.
        """
        return self.context.has_dossiers_to_archive()
