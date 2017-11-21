from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone import api


class SetTaskCommentPermission(UpgradeStep):
    """Set task comment permission.
    """

    def __call__(self):
        self.install_upgrade_profile()

        # Merge update security from
        # - 20161125103319@opengever.dossier:default
        # - 20170301235934@opengever.dossier:default

        # Also reindex security since, 20161125103319@opengever.dossier:default
        # probably indexed the security
        self.update_workflow_security(
            ['opengever_dossier_workflow'],
            reindex_security=self.has_offered_or_archived_dossiers())

    def has_offered_or_archived_dossiers(self):
        return bool(api.content.find(
            object_provides=IDossierMarker,
            review_state=['dossier-state-offered', 'dossier-state-archived']))
