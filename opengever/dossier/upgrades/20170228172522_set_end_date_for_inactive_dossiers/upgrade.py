from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone import api


class SetEndDateForInactiveDossiers(UpgradeStep):
    """Set end date for inactive dossiers.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.wf_tool = api.portal.get_tool('portal_workflow')

        for dossier in self.objects(
                {'object_provides': IDossierMarker.__identifier__,
                 'review_states': 'dossier-state-inactive'},
                'Set endate for inactive dossiers'):

            self.set_end_date(dossier)

    def set_end_date(self, dossier):
        if not IDossier(dossier).end:
            IDossier(dossier).end = self.get_last_deactivation_date(dossier)

    def get_last_deactivation_date(self, dossier):
        workflow_id = self.wf_tool.getWorkflowsFor(dossier)[0].getId()
        history = self.wf_tool.getHistoryOf(workflow_id, dossier)
        for entry in reversed(history):
            if entry.get('review_state') == 'dossier-state-inactive':
                return entry.get('time').asdatetime().date()
