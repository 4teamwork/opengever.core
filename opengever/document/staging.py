
from five import grok
from zope.event import notify
from zope.interface import Interface

from Products.statusmessages.interfaces import IStatusMessage

from opengever.document.document import IDocumentSchema
from opengever.document.events import ObjectCheckedOutEvent, ObjectCheckedInEvent


class CheckoutNotAllowed(Exception):
    __doc__ = 'Checkout is not allowed'



class CheckinNotAllowed(Exception):
    __doc__ = 'Checkin is not allowed'



class ICheckinCheckoutManager(Interface):
    pass



class CheckinCheckoutManager(grok.Adapter):
    grok.context(IDocumentSchema)
    grok.implements(ICheckinCheckoutManager)
    grok.require('zope2.View')

    def __init__(self, context):
        self.context = context
        self.request = context.REQUEST

    @property
    def checkout_allowed(self):
        # XXX implement me
        return True

    @property
    def checkin_allowed(self):
        # XXX implement me
        return True

    def checkout(self, comment='', show_status_message=True):
        if not self.checkout_allowed:
            raise CheckOutNotAllowed
        # XXX check it out
        # create status message
        if show_status_message:
            msg = 'Could not checkout %s: implementation missing' % \
                self.context.Title()
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
        # trigger event
        notify(ObjectCheckedOutEvent(self.context, comment))

    def checkin(self, comment='', show_status_message=True):
        if not self.checkin_allowed:
            raise CheckInNotAllowed
        # XXX check it in
        # create status message
        if show_status_message:
            msg = 'Could not checkin %s: implementation missing' % \
                self.context.Title()
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
        # trigger event
        notify(ObjectCheckedInEvent(self.context, comment))

