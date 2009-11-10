

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
from opengever.document import _


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
    def contains_checkoutable_children(self):
        for obj in self.context.getFolderContents():
            if ICheckinCheckoutManager(obj).checkout_allowed:
                return True
        return False

    @property
    def contains_checkinable_children(self):
        for obj in self.context.getFolderContents():
            if ICheckinCheckoutManager(obj).checkin_allowed:
                return True
        return False

    @property
    def contains_cancable_children(self):
        for obj in self.context.getFolderContents():
            if ICheckinCheckoutManager(obj).cancel_allowed:
                return True
        return False

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
        comment = comment or ''
        context = aq_inner(self.context)
        if not self.checkout_allowed:
            if show_status_message:
                msg = _(u'Could not checkout: ${title}, checkout not allowed',
                        mapping={'title':self.context.Title()})
                IStatusMessage(self.request).addStatusMessage(msg, type='error')
                return
            else:
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
        wc.reindexObject()
        # create status message
        if show_status_message:
            msg = _(u'Checked out: ${title}',
                    mapping={'title':self.context.Title()})
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
        # trigger event
        notify(ObjectCheckedOutEvent(context, comment))

    def checkin(self, comment='', show_status_message=True):
        context = aq_inner(self.context)
        if not self.checkin_allowed:
            if show_status_message:
                msg = _(u'Could not checkin: ${title}, checkin not allowed',
                        mapping={'title':self.context.Title()})
                IStatusMessage(self.request).addStatusMessage(msg, type='error')
                return
            else:
                raise CheckInNotAllowed
        # check it in
        policy = ICheckinCheckoutPolicy(context)
        baseline = policy.checkin(comment)
        baseline.reindexObject()
        # create status message
        if show_status_message:
            msg = _(u'Checked in: ${title}',
                    mapping={'title':baseline.Title()})
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
        # trigger event
        notify(ObjectCheckedInEvent(baseline, comment))

    def cancel(self, show_status_message=True):
        context = aq_inner(self.context)
        if not self.cancel_allowed:
            if show_status_message:
                msg = _(u'Could not cancel checkin: ${title}, not allowed',
                        mapping={'title':self.context.Title()})
                IStatusMessage(self.request).addStatusMessage(msg, type='error')
                return
            else:
                raise CancelNotAllowed
        # cancel checkout
        policy = ICheckinCheckoutPolicy(context)
        baseline = policy.cancelCheckout()
        baseline.reindexObject()
        if show_status_message:
            msg = _(u'Checkout canceled: ${title}',
                    mapping={'title':baseline.Title()})
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
        notify(ObjectCheckoutCanceledEvent(baseline))
