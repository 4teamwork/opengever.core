from ftw.upgrade import UpgradeStep


class RemoveCheckoutEditAndCancelActions(UpgradeStep):
    """Remove checkout edit and cancel actions.
    """

    def __call__(self):
        self.actions_remove_type_action(
            'opengever.meeting.sablontemplate', "checkout_edit_document")
        self.actions_remove_type_action(
            'opengever.meeting.sablontemplate', "cancel_document_checkout")

        self.actions_remove_type_action(
            'opengever.meeting.proposaltemplate', "checkout_edit_document")
        self.actions_remove_type_action(
            'opengever.meeting.proposaltemplate', "cancel_document_checkout")
