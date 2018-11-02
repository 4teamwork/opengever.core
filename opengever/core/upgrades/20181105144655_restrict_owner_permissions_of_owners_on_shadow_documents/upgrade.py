from ftw.upgrade import UpgradeStep


class RestrictOwnerPermissionsOfOwnersOnShadowDocuments(UpgradeStep):
    """Restrict owner permissions of owners on shadow documents."""

    def __call__(self):
        self.install_upgrade_profile()
        query = {'portal_type': 'opengever.document.document', 'review_state': 'document-state-shadow'}
        for shadow_document in self.objects(query, "Ensure correct roles and permissions on shadow documents."):
            self.update_security(shadow_document, reindex_security=False)
