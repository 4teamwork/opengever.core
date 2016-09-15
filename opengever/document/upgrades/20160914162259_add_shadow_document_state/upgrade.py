from ftw.upgrade import UpgradeStep


class AddShadowDocumentState(UpgradeStep):
    """Add shadow document state.
    """

    def __call__(self):
        self.install_upgrade_profile()
        # when this upgrade run, no documents can be in the new state yet
        self.update_workflow_security(['opengever_document_workflow'],
                                      reindex_security=False)
