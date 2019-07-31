from opengever.document.behaviors import IBaseDocument
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IFileActions
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from plone import api
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IFileActions)
@adapter(IBaseDocument, Interface)
class BaseDocumentFileActions(object):
    """Define availability for actions and action sets on IBaseDocument.

    Methods should return availability for one single action.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_edit_metadata_action_available(self):
        return api.user.has_permission(
            'Modify portal content',
            obj=self.context)

    def is_any_checkout_or_edit_available(self):
        return False

    def is_oc_direct_checkout_action_available(self):
        return False

    def is_oc_direct_edit_action_available(self):
        return False

    def is_oc_zem_checkout_action_available(self):
        return False

    def is_oc_zem_edit_action_available(self):
        return False

    def is_oc_unsupported_file_checkout_action_available(self):
        return False

    def is_checkin_without_comment_available(self):
        return False

    def is_checkin_with_comment_available(self):
        return False

    def is_cancel_checkout_action_available(self):
        return False

    def is_download_copy_action_available(self):
        return self.context.has_file()

    def is_attach_to_email_action_available(self):
        return (
            is_officeconnector_attach_feature_enabled()
            and self.context.has_file())

    def is_oneoffixx_retry_action_available(self):
        return False


@implementer(IFileActions)
@adapter(IDocumentSchema, Interface)
class DocumentFileActions(BaseDocumentFileActions):

    def is_versioned(self):
        return self.request.get('version_id') is not None

    def is_any_checkout_or_edit_available(self):
        return (
            not self.is_versioned()
            and self.context.has_file()
            and self.context.is_checkout_and_edit_available())

    def is_edit_metadata_action_available(self):
        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        return (
            super(DocumentFileActions, self).is_edit_metadata_action_available()
            and not manager.is_locked()
            and not manager.is_checked_out_by_another_user()
            )

    def is_oc_direct_checkout_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and self.context.is_office_connector_editable()
                and not self.context.is_checked_out()
                and is_officeconnector_checkout_feature_enabled())

    def is_oc_direct_edit_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and self.context.is_office_connector_editable()
                and self.context.is_checked_out()
                and is_officeconnector_checkout_feature_enabled())

    def is_oc_zem_checkout_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and self.context.is_office_connector_editable()
                and not self.context.is_checked_out()
                and not is_officeconnector_checkout_feature_enabled())

    def is_oc_zem_edit_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and self.context.is_office_connector_editable()
                and self.context.is_checked_out()
                and not is_officeconnector_checkout_feature_enabled())

    def is_oc_unsupported_file_checkout_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and not self.context.is_office_connector_editable()
                and not self.context.is_checked_out())

    def is_checkin_without_comment_available(self):
        return (not self.is_versioned()
                and self.is_checkin_with_comment_available()
                and not self.context.is_locked())

    def is_checkin_with_comment_available(self):
        return (not self.is_versioned()
                and self.context.has_file()
                and self.context.is_checkin_allowed())

    def is_cancel_checkout_action_available(self):
        if not self.context.has_file():
            return False

        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        return manager.is_cancel_allowed()

    def is_download_copy_action_available(self):
        """Disable downloading copies when the document is checked out by
        another user.
        """
        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        return (
            super(DocumentFileActions, self).is_download_copy_action_available()
            and not manager.is_checked_out_by_another_user())

    def is_attach_to_email_action_available(self):
        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        return (
            super(DocumentFileActions, self).is_attach_to_email_action_available()
            and not manager.is_checked_out_by_another_user()
            )

    def is_oneoffixx_retry_action_available(self):
        return self.context.is_oneoffixx_creatable()
