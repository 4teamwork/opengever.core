from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.response import IResponseContainer
from opengever.locking.lock import MEETING_SUBMITTED_LOCK
from opengever.meeting import _
from opengever.meeting.proposalhistory import ProposalResponse
from plone.locking.interfaces import ILockable
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import NotFound


class UnlockSubmittedDocumentForm(BrowserView):

    def __call__(self):
        if not self.context.is_submitted_document():
            raise NotFound()

        if not ILockable(self.context).locked():
            return self.reload_context_default_view()

        if self.request.get('form.buttons.cancel'):
            return self.reload_context_default_view()

        if self.request.get('form.buttons.unlock'):
            self.unlock()
            self.add_response_object()

            msg = _('statmsg_submitted_document_unlocked',
                    default=u'Document has been unlocked',)
            IStatusMessage(self.request).addStatusMessage(msg, type='info')

            if self.is_js_request():
                """prepOverlay requires a template without the form. Just rendering
                the template without the form will not work because of the portal
                messages. Rendering the default template is consuming
                the portal messages. After the pagereload indicated by
                prepOverlay the user won't see any portalmessage.

                So we're just returning an empty div.
                """
                return '<div></div>'
            else:
                """If js is broken or if the user requested this view directly,
                we have to reload the page after successfully unlocking the
                document.
                """
                return self.reload_context_default_view()
        return super(UnlockSubmittedDocumentForm, self).__call__()

    def unlock(self):
        ILockable(self.context).unlock(MEETING_SUBMITTED_LOCK)

    def reload_context_default_view(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def is_js_request(self):
        """By default, this form is rendered through prepOverlay which makes an
        ajax-request to this view to fetch the form content.

        See prepoverlay.js for more information about the js-implementation.

        If js is broken or the view is requested directly by the user, this
        function will return False.
        """
        return self.request.get('ajax_load', False)

    def show_form(self):
        return self.is_form_submitted() and self.is_js_request()

    def add_response_object(self):
        response = ProposalResponse(
            u'document_unlocked',
            document_title=self.context.title,
            )

        proposal = aq_parent(aq_inner(self.context))
        IResponseContainer(proposal).add(response)
