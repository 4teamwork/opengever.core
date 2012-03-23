from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone.interfaces import IPloneSiteRoot
from five import grok
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility


FILING_NO_KEY = "filing_no"


class FilingNumberMaintenance(grok.View):
    grok.name('filing_number_maintenance')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def render(self):
        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)
        if ann:
            mapping = ann.get(FILING_NO_KEY)
            return mapping
        return 'NO mapping Exist'
