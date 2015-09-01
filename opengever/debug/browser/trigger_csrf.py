from five import grok
from Products.CMFPlone.interfaces import IPloneSiteRoot


class TriggerCSRF(grok.View):
    """A view to trigger a plone.protect confirmation dialog.
    """

    grok.name('trigger-csrf')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def __call__(self):
        plone = self.context

        # Cause a write in a GET request
        plone.some_fancy_attribute = True

        return super(TriggerCSRF, self).__call__()
