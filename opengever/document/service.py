from opengever.document import _
from plone import api
from plone.rest import Service
from zExceptions import Forbidden
from zope.i18n import translate
import json


class OfficeatworkInitializationLabels(Service):
    """Provide an HTTP GET endpoint for officeatwork initialization related labels for shadow documents."""

    def render(self):
        """Provide i18n labels for officeatwork initialization for shadow documents."""
        if self.context.is_shadow_document():
            title = translate(
                _(u'label_officeatwork_init_title', default=u'Initializing officeatwork'),
                context=self.request,
                )

            message = translate(
                _(u'msg_officeatwork_init', default=u'Please wait.'),
                context=self.request,
            )

            payload = dict(
                title=title,
                message=message,
            )

            return json.dumps(payload)

        # Fail per default
        raise Forbidden


class OfficeatworkRetryAbortLabels(Service):
    """Provide an HTTP GET endpoint for officeatwork retry/abort logic related labels for shadow documents."""

    def render(self):
        """Provide i18n labels for officeatwork retry/abort logic for shadow documents."""
        if self.context.is_shadow_document():
            retry = translate(
                _(u'label_retry', default=u'Retry'),
                context=self.request,
            )

            abort = translate(
                _(u'label_abort', default=u'Abort'),
                context=self.request,
            )

            payload = dict(
                retry=retry,
                abort=abort,
            )

            return json.dumps(payload)

        # Fail per default
        raise Forbidden


class ShadowDocumentDeleteConfirmMessage(Service):
    """Provide an HTTP GET endpoint for shadow document deletion information."""

    def render(self):
        """Provide i18ns label for a user facing alert box for confirming shadow document deletion."""
        if self.context.is_shadow_document():
            message = translate(
                _(u'msg_shadow_document_delete_confirm_message', default=u'Do you really want to delete this document?'),
                context=self.request,
                )

            title = translate(
                _(u'label_shadow_document_delete_confirm_title', default=u'Delete document'),
                context=self.request,
                )

            label_yes = translate(
                _(u'label_yes', default=u'yes'),
                context=self.request,
                )

            label_no = translate(
                _(u'label_no', default=u'no'),
                context=self.request,
                )

            payload = dict(
                message=message,
                title=title,
                label_yes=label_yes,
                label_no=label_no,
                )

            return json.dumps(payload)

        # Fail per default
        raise Forbidden


class DeleteShadowDocument(Service):
    """Provide a HTTP DELETE endpoint for shadow documents."""

    def render(self):
        """Delete a shadow document.

        Preconditions:
        * Only the document owner or a Manager may delete a shadow document
        * Only a document still in the shadow state may be deleted
        * Only a document without a file may be deleted
        * Only a document without versions beyond the initial version may be deleted
        """
        document_owner_id = self.context.owner_info().get('id', None)

        current_user = api.user.get_current()
        current_user_id = current_user.id

        # The creator or someone with a Manager role is trying to delete the document
        if (document_owner_id and current_user_id == document_owner_id) or api.user.has_permission('Manage portal', obj=self.context):
            # The document is still in a shadow state
            if self.context.is_shadow_document():
                # The document does not yet have a file
                if not self.context.file:
                    # The document does not yet have versions
                    if self.context.version_id == 0:
                        parent_dossier = self.context.get_parent_dossier()
                        parent_dossier_url = parent_dossier.absolute_url() if parent_dossier else None

                        parent_inbox = self.context.get_parent_inbox()
                        parent_inbox_url = parent_inbox.absolute_url() if parent_inbox else None

                        parent_url = parent_dossier_url if parent_dossier_url else parent_inbox_url

                        api.content.delete(obj=self.context)

                        success_message = _(u'label_succesful_shadow_document_deletion', default='Succesfully deleted the shadow document.')
                        api.portal.show_message(message=success_message, type='info', request=self.request)

                        return json.dumps(dict(parent_url=parent_url))

        # Fail per default
        failure_message = _(u'label_failed_shadow_document_deletion', default='Failed to delete the shadow document.')
        api.portal.show_message(message=failure_message, type='error', request=self.request)
        raise Forbidden
