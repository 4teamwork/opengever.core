from ftw.upgrade import UpgradeStep
from plone import api


class RemoveTabbedViewActions(UpgradeStep):
    """Remove tabbed view actions.
    """

    tabbeview_action_ids = [
        'overview',
        'subdossiers',
        'documents-proxy',
        'tasks',
        'proposals',
        'participants',
        'trash-proxy',
        'journal',
        'sharing',
        'tasktemplatefolders',
        'sablontemplates'
    ]

    def __call__(self):
        for fti in self.get_dossier_types():
            self.remove_tabbedview_actions(fti)

    def remove_tabbedview_actions(self, fti):
        for action_id in self.tabbeview_action_ids:
            self.actions_remove_type_action(fti.id, action_id)

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
