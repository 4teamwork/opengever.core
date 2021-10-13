from ftw.upgrade import UpgradeStep
from plone import api


class ReplaceNameFromTitleBehaviorForTemplateFolders(UpgradeStep):
    """Replace name from title behavior for template folders.
    """

    def __call__(self):
        self.install_upgrade_profile()

        query = {'portal_type': ['opengever.contact.contactfolder',
                                 'opengever.dossier.templatefolder',
                                 'opengever.inbox.container',
                                 'opengever.inbox.inbox',
                                 'opengever.meeting.committeecontainer',
                                 ]}
        catalog = api.portal.get_tool('portal_catalog')
        for obj in self.objects(query, "Reindex object_provides."):
            catalog.reindexObject(obj, idxs=['object_provides'],
                                  update_metadata=False)
