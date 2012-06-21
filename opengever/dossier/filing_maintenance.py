from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Transience.Transience import Increaser
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from five import grok
from opengever.dossier.behaviors.dossier import IDossierMarker
from persistent.dict import PersistentDict
from plone.directives import form
from z3c.form import button, field
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import Interface
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


class IFilingNumberRowSchema(Interface):
    key = schema.TextLine(title=u"Key")
    counter = schema.Int(title=u"Increaser Value")


class IFilingNumberCountersFormSchema(Interface):
    counters = schema.List(
        title=u"counters",
        value_type=DictRow(title=u"counter", schema=IFilingNumberRowSchema)
        )


@form.default_value(field=IFilingNumberCountersFormSchema['counters'])
def set_counters(data):
    portal = getUtility(ISiteRoot)
    ann = IAnnotations(portal)

    if FILING_NO_KEY in ann.keys():
        entries = []
        for k, v in ann.get(FILING_NO_KEY).items():
            entries.append({'key': k, 'counter': v.value})
        return entries

    else:
        return {}


class FilingNumberCountersForm(form.Form):
    grok.context(IPloneSiteRoot)
    grok.name('filingnumber-adjustment')
    grok.require('zope2.View')

    fields = field.Fields(IFilingNumberCountersFormSchema)
    fields['counters'].widgetFactory = DataGridFieldFactory

    ignoreContext = True

    @button.buttonAndHandler(u'Save')
    def archive(self, action):
        data, errors = self.extractData()

        if len(errors) > 0:
            return

        portal = getUtility(ISiteRoot)
        ann = IAnnotations(portal)
        if FILING_NO_KEY not in ann.keys():
            ann[FILING_NO_KEY] = PersistentDict()

        for row in data.get('counters'):
            ann[FILING_NO_KEY][row.get('key')] = Increaser(row.get('counter'))

        return self.request.RESPONSE.redirect(self.context.absolute_url())
