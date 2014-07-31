from ftw.upgrade import UpgradeStep


class RemoveAttachRemoteDocumentAction(UpgradeStep):

    def __call__(self):
        self.actions_remove_type_action(
            'opengever.task.task', 'attach_remote_document')
