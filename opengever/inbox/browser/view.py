from opengever.base.browser.default_view import OGDefaultView
from opengever.inbox import _
from opengever.ogds.base.utils import get_current_org_unit
from Products.statusmessages.interfaces import IStatusMessage


class InboxContainerView(OGDefaultView):

    def render(self):
        current_inbox = self.context.get_current_inbox()

        if current_inbox:
            return self.request.RESPONSE.redirect(current_inbox.absolute_url())
        else:
            msg = _(
                u'current_inbox_not_available',
                u'Your not allowed to access the inbox of ${current_org_unit}',
                mapping={'current_org_unit': get_current_org_unit().label()})

            IStatusMessage(self.request).addStatusMessage(msg, type='warning')

        return super(InboxContainerView, self).render()
