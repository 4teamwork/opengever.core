from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import queryMultiAdapter
from zope.publisher.browser import BrowserView


class CheckinCheckoutController(BrowserView):
    """The controller view gives infos about the current document
    concerning checkin / checkout.
    """

    def is_checkout_allowed(self):
        """Checks whether checkout is allowed or not.
        """
        if self.context.digitally_available:

            manager = queryMultiAdapter(
                (self.context, self.request),
                ICheckinCheckoutManager,
                )

            if manager:
                return manager.is_checkout_allowed()

        return False

    def is_checkin_allowed(self):
        """Checks whether checkin is allowed or not.
        """
        manager = queryMultiAdapter(
            (self.context, self.request),
            ICheckinCheckoutManager,
            )

        if manager:
            return manager.is_checkin_allowed()

        return False

    def is_cancel_allowed(self):
        """Checks whether cancelling a checkout is allowed or not.
        """
        manager = queryMultiAdapter(
            (self.context, self.request),
            ICheckinCheckoutManager,
            )

        if manager:
            return manager.is_cancel_allowed()

        return False

    def is_locked(self):
        """Check if the document is locked."""
        manager = queryMultiAdapter(
            (self.context, self.request),
            ICheckinCheckoutManager,
            )

        if manager:
            return manager.is_locked()

        return False
