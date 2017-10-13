from opengever.document import _
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

