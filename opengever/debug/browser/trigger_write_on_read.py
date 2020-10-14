from Products.Five import BrowserView


class TriggerWriteOnRead(BrowserView):
    """A view to trigger a write-on-read.

    This can be used to trigger a plone.protect confirmation dialog when
    example, or debugging other behavior associated with writes-on-read.
    """

    def __call__(self):
        plone = self.context

        # Cause a write in a GET request
        plone.some_fancy_attribute = True

        return super(TriggerWriteOnRead, self).__call__()
