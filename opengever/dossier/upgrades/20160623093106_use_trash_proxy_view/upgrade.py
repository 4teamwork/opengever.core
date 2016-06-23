from ftw.upgrade import UpgradeStep
from plone import api


class UseTrashProxyView(UpgradeStep):
    """Use trash proxy view.
    """

    old_action_id = 'trash'
    new_action_id = 'trash-proxy'

    def __call__(self):
        self.install_upgrade_profile()
        self.change_trashtab_to_trash_proxy_tab()

    def _is_dossier_fti(self, fti):
        """Use the opengever.dossier.behaviors.dossier.IDossier behavior to
        detect if the FTI is a dossier fti. That behavior is enabled for all
        currently known dossiers.
        """

        behaviors = fti.getProperty('behaviors')
        if not behaviors:
            return False

        return 'opengever.dossier.behaviors.dossier.IDossier' in behaviors

    def change_trashtab_to_trash_proxy_tab(self):
        """To choose which template the user has selected before (list or gallery)
        with activated bumblebeefeature, we have to add a proxy view.

        The tabs are stored in actions. So we have to update them to the new
        proxy-view.
        """
        ttool = api.portal.get_tool('portal_types')
        for fti in ttool.listTypeInfo():
            if not self._is_dossier_fti(fti):
                continue

            for action in fti._actions:
                if not action.id == self.old_action_id:
                    continue

                action.id = self.new_action_id
