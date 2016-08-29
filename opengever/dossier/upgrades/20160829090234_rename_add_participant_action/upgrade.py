from ftw.upgrade import UpgradeStep
from plone import api


class RenameAddParticipantAction(UpgradeStep):
    """Rename add participant action.
    """

    def __call__(self):
        for fti in self.get_dossier_types():
            for action in fti._actions:
                if action.id == 'add_participant':
                    action.title = 'Participant'

    def get_dossier_types(self):
        ttool = api.portal.get_tool('portal_types')
        for fti in ttool.listTypeInfo():
            if self._is_dossier_fti(fti):
                yield fti

    def _is_dossier_fti(self, fti):
        """Use the opengever.dossier.behaviors.dossier.IDossier behavior to
        detect if the FTI is a dossier fti. That behavior is enabled for all
        currently known dossiers.
        """

        behaviors = fti.getProperty('behaviors')
        if not behaviors:
            return False

        return 'opengever.dossier.behaviors.dossier.IDossier' in behaviors
