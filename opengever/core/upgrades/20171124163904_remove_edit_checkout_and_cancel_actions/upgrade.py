from ftw.upgrade import UpgradeStep


class RemoveEditCheckoutAndCancelActions(UpgradeStep):
    """Remove edit checkout and cancel actions.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.actions_remove_type_action(
            'opengever.document.document', "checkout_edit_document")
        self.actions_remove_type_action(
            'opengever.document.document', "cancel_document_checkout")
