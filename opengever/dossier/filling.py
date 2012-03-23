from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from opengever.dossier.behaviors.dossier import IDossierMarker
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility


FILING_NO_KEY = "filing_no"


class FilingNumberMaintenance(BrowserView):

    def print_mapping(self):
        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)
        if ann:
            mapping = ann.get(FILING_NO_KEY)
            for k, v in mapping.items():
                self.request.RESPONSE.write(
                    '%s: %i' % (k.encode('utf-8'), v.value))

    def print_filing_numbers(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        import pdb; pdb.set_trace()
