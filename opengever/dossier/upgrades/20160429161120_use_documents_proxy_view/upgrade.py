from ftw.upgrade import UpgradeStep
from plone import api


class UseDocumentsProxyView(UpgradeStep):
    """Use documents proxy view.
    """

    dossier_types = [
        'opengever.dossier.businesscasedossier',
        'opengever.dossier.templatedossier',
        'opengever.dossier.projectdossier'
        ]

    old_action_id = 'documents'
    new_action_id = 'documents-proxy'

    def __call__(self):
        self.install_upgrade_profile()
        self.change_documents_tab_to_docuemnts_proxy_tab()

    def change_documents_tab_to_docuemnts_proxy_tab(self):
        """To choose which template the user has selected before (list or gallery)
        with activated bumblebeefeature, we have to add a proxy view.

        The tabs are stored in actions. So we have to update them to the new
        proxy-view.
        """
        ttool = api.portal.get_tool('portal_types')
        for dossier_type in self.dossier_types:
            dossier = ttool.get(dossier_type)
            if not dossier:
                continue

            for action in dossier._actions:
                if not action.id == self.old_action_id:
                    continue

                action.id = self.new_action_id
