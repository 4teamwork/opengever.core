from ftw.upgrade import UpgradeStep


class AddRemovedState(UpgradeStep):
    """Add document-state-removed to the document workflow
    and updates workflow security.
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.document.upgrades:4100')

        self.update_workflow_security(['opengever_document_workflow'],
                                      reindex_security=False)
