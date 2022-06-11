from ftw.upgrade import UpgradeStep


# from opengever.dossier.behaviors.dossier import IDossierMarker
# from plone import api


class LetArchivistSeeOfferedAndArchivedDossiers(UpgradeStep):
    """Let archivist see offered and archived dossiers.
    """

    def __call__(self):
        self.install_upgrade_profile()

    # Moved to 20170328131435@opengever.dossier:default

    #     self.update_workflow_security(
    #         ['opengever_dossier_workflow'],
    #         reindex_security=self.has_offered_or_archived_dossiers())

    # def has_offered_or_archived_dossiers(self):
    #     return bool(api.content.find(
    #         object_provides=IDossierMarker,
    #         review_state=['dossier-state-offered', 'dossier-state-archived']))
