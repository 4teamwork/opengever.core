from opengever.dossier.behaviors.dossier import IDossierMarker
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.schema.vocabulary import getVocabularyRegistry


FILING_NO_KEY = "filing_no"


class FilingNumberMaintenance(BrowserView):

    def log(self, msg):
        self.request.RESPONSE.write(msg)

    def print_mapping(self):
        """Return the actual filingnumber mapping"""

        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)
        if ann:
            mapping = ann.get(FILING_NO_KEY)
            for k, v in mapping.items():
                self.log(
                    '%s: %i\n' % (k.encode('utf-8'), v.value))

    def print_filing_numbers(self):
        """Return a set of all filingnumbers the are used """

        catalog = getToolByName(self.context, 'portal_catalog')

        dossiers = catalog(object_provides=IDossierMarker.__identifier__)
        filing_numbers = [a.filing_no for a in dossiers if a.filing_no]
        filing_numbers = list(set(filing_numbers))
        filing_numbers.sort()
        temp = ''
        for no in filing_numbers:
            key = '-'.join(no.split('-')[:-1])
            if key != temp:
                self.log(' -------------------------------- \n')
                temp = key
            self.log(no.encode('utf-8') + '\n')

    def print_filing_prefixes(self):
        """Reutrns all filing prefixes and their translations"""
        voca = getVocabularyRegistry().get(
            self.context, 'opengever.dossier.type_prefixes')

        for term in voca:
            self.log('%s: %s' % (term.value, term.title))
