from Products.Five import BrowserView


class TriggerCSRF(BrowserView):
    """A view to trigger a plone.protect confirmation dialog.
    """

    def __call__(self):
        plone = self.context

        # Cause a write in a GET request
        plone.some_fancy_attribute = True

        return super(TriggerCSRF, self).__call__()
