
from Acquisition import aq_inner
from five import grok
from zope.event import notify
from zope.interface import Interface

from Products.statusmessages.interfaces import IStatusMessage

from plone.app.iterate.interfaces import ICheckinCheckoutPolicy

from opengever.document.document import IDocumentSchema
from opengever.document.events import ObjectCheckedOutEvent
from opengever.document.events import ObjectCheckedInEvent
from opengever.document.events import ObjectCheckoutCanceledEvent


class CheckoutNotAllowed(Exception):
    __doc__ = 'Checkout is not allowed'


class CheckinNotAllowed(Exception):
    __doc__ = 'Checkin is not allowed'


class CancelNotAllowed(Exception):
    __doc__ = 'Cancel is not allowed'


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
        if not self.context.restrictedTraverse('iterate_control').checkout_allowed():
            return False
        # XXX implement me
        return True

    @property
    def checkin_allowed(self):
        if not self.context.restrictedTraverse('iterate_control').checkin_allowed():
            return False
        # XXX implement me
        return True

    @property
    def cancel_allowed(self):
        iterate_control = self.context.restrictedTraverse('iterate_control')
        if not iterate_control.cancel_allowed():
            return False
        # XXX implement me
        return True

    def checkout(self, comment='', show_status_message=True):
        context = aq_inner(self.context)
        if not self.checkout_allowed:
            raise CheckOutNotAllowed
        # get the plone.app.iterate containers
        checkout_view = self.context.restrictedTraverse('content-checkout')
        containers = list(checkout_view.containers())
        # choose locator, we use the first one since we expect only one container
        locator = containers[0]['locator']
        # check it out
        policy = ICheckinCheckoutPolicy(context)
        wc = policy.checkout(locator())
        # we need to reindex context (eliminate some side effects)
        context.reindexObject()
        # create status message
        if show_status_message:
            msg = 'Checked out %s' % \
                context.Title()
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
        # trigger event
        notify(ObjectCheckedOutEvent(context, comment))

    def checkin(self, comment='', show_status_message=True):
        context = aq_inner(self.context)
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

    def cancel(self):
        context = aq_inner(self.context)
        if not self.cancel_allowed:
            raise CancelNotAllowed
        # XXX cancel checkout
        notify(ObjectCheckoutCanceledEvent(context))
