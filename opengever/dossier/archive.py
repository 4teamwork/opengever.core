from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

from Acquisition import aq_inner, aq_parent
from persistent.dict import PersistentDict
from five import grok
from z3c.form import form, button, field
from Products.CMFCore.interfaces import ISiteRoot
from Products.Transience.Transience import Increaser

from plone.z3cform import layout
from plone.registry.interfaces import IRegistry


from opengever.dossier import _
from opengever.dossier.base import IDossierContainerTypes
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.base.interfaces import IBaseClientID


@grok.provider(IContextSourceBinder)
def get_filing_prefixes(context):
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IDossierContainerTypes)
    prefixes = getattr(proxy, 'type_prefixes')
    filing_prefixes = [SimpleTerm (value, value, value) for value in prefixes]

    return SimpleVocabulary(filing_prefixes)


class IArchiveFormSchema(Interface):

    filing_prefix = schema.Choice(
            title = _(u'filing_prefix', default="filing prefix"),
            source = get_filing_prefixes,
            required = True,
    )
    
    filing_year = schema.Int(
        title = _(u'filing_year', default="filing Year"),
        required = True,
    )
        
class ArchiveForm(form.Form):
    fields = field.Fields(IArchiveFormSchema)
    ignoreContext = True
    label = _(u'heading_archive_form', u'Archive Dossier')

    @button.buttonAndHandler(_(u'button_archive', default=u'Archive'))
    def archive(self, action):
        data, errors = self.extractData()
        if len(errors)==0:
            FILING_NO_KEY = "filing_no"

            filing_year = str(data.get('filing_year')) 
            filing_prefix = data.get('filing_prefix')

            # filing_sequence
            key = filing_prefix + "-" + filing_year
            portal = getUtility(ISiteRoot)
            ann = IAnnotations(portal)
            if FILING_NO_KEY not in ann.keys():
                ann[FILING_NO_KEY] = PersistentDict()
            map = ann.get(FILING_NO_KEY)
            if key not in map:
                map[key] = Increaser(0)
            # increase
            inc = map[key]
            inc.set(inc()+1)
            map[key] = inc
            filing_sequence = inc()

            # filing_client
            registry = getUtility(IRegistry)
            proxy = registry.forInterface(IBaseClientID)
            filing_client = getattr(proxy, 'client_id')
            
            # filing_no
    
            filing_no = filing_client + "-" + filing_prefix + "-" + filing_year + "-" + str(filing_sequence)
            self.context.filing_no = filing_no
            
            subdossiers = self.context.portal_catalog(
                                    portal_type="opengever.dossier.businesscasedossier",
                                    path=dict(depth=1,
                                        query='/'.join(self.context.getPhysicalPath()),
                                    ),
                                    sort_on='modified',
                                    sort_order='reverse',
            )
            
            counter = 1
            for dossier in subdossiers:
                dossier = dossier.getObject()
                dossier.filing_no = filing_no + "." + str(counter)
                counter += 1
            
            return self.request.RESPONSE.redirect(self.context.absolute_url() + '/content_status_modify?workflow_action=dossier-transition-archive')


class ArchiveFormView(layout.FormWrapper, grok.CodeView):
    grok.context(IDossierMarker)
    grok.name('transition-archive')
    grok.require('zope2.View')
    form = ArchiveForm
    
    #label = _(u'heading_archive_form', u'Archive Dossier')
    
    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)

    def render(self):
        raise NotImplemented

    def __call__(self, *args, **kwargs):
        parent = aq_parent(aq_inner(self.context))
        if IDossierMarker.providedBy(parent):
            self.request.RESPONSE.redirect(self.context.absolute_url() + '/content_status_modify?workflow_action=dossier-transition-archive')
        return layout.FormWrapper.__call__(self, *args, **kwargs)
