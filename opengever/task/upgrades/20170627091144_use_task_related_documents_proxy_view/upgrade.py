from ftw.upgrade import UpgradeStep
from plone import api


class UseRelatedDocumentsProxyView(UpgradeStep):
    """Use related documents proxy view.
    """

    old_action_id = 'relateddocuments'
    new_action_id = 'relateddocuments-proxy'

    type_names = ['opengever.task.task',
                  'opengever.inbox.forwarding']

    def __call__(self):
        self.install_upgrade_profile()
        self.change_relateddocuments_tab_to_relateddocuments_proxy_tab()

    def change_relateddocuments_tab_to_relateddocuments_proxy_tab(self):
        """To choose which template the user has selected before (list or gallery)
        with activated bumblebeefeature, we have to add a proxy view.

        The tabs are stored in actions. So we have to update them to the new
        proxy-view.
        """
        ttool = api.portal.get_tool('portal_types')
        for type_name in self.type_names:
            fti = ttool[type_name]
            for action in fti._actions:
                if not action.id == self.old_action_id:
                    continue

                action.id = self.new_action_id
