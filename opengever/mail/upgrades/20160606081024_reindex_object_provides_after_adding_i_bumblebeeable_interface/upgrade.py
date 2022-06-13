from ftw.upgrade import UpgradeStep


# from plone import api


class ReindexObjectProvidesAfterAddingIBumblebeeableInterface(UpgradeStep):
    """Reindex object_provides after adding IBumblebeeable interface.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # Moved to 20170411113233@opengever.base:default
        # This PR indexes already another index

        # catalog = api.portal.get_tool('portal_catalog')
        # query = {'portal_type': 'ftw.mail.mail'}
        # msg = 'Reindex object_provides for mails.'

        # for obj in self.objects(query, msg):
        #     catalog.reindexObject(
        #         obj, idxs=['object_provides'], update_metadata=False)
