from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from plone import api


class AddMacroEnabledOfficeMimetypes(UpgradeStep):

    def __call__(self):
        # Install the opengever.policy.base:mimetype profile.
        # This initializes the previously unset profile version and
        # registers the newly added macro enabled office mimetypes.
        self.setup_install_profile('profile-opengever.policy.base:mimetype')
        self._update_document_metadata()

    def _update_document_metadata(self):
        """Update the getIcon metadata on documents.
        """
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type='opengever.document.document')

        # A getIcon value of 'application.png' indicates that the mimetype
        # coulnd't be resolved for this document - only consider these
        brains = filter(lambda b: b.getIcon == 'application.png', brains)

        msg = 'Reindexing getIcon metadata for documents'
        with ProgressLogger(msg, brains) as step:
            for brain in brains:
                catalog.reindexObject(
                    brain.getObject(), idxs=['getIcon'], update_metadata=1)
                step()
