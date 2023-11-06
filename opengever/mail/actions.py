from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.document.actions import BaseDocumentContextActions
from opengever.mail.mail import IOGMailMarker
from zope.component import adapter


@adapter(IOGMailMarker, IOpengeverBaseLayer)
class MailContextActions(BaseDocumentContextActions):

    def get_actions(self):
        super(MailContextActions, self).get_actions()
        self.maybe_add_extract_attachments()
        return self.actions

    def maybe_add_extract_attachments(self):
        if self.is_extract_attachments_available():
            self.add_action(u'extract_attachments')

    def is_extract_attachments_available(self):
        return self.context.can_extract_attachments_to_parent()

    def is_oc_view_available(self):
        return True
