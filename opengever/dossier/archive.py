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
from z3c.form.interfaces import INPUT_MODE
from z3c.form.browser import radio
from Products.CMFCore.interfaces import ISiteRoot
from Products.Transience.Transience import Increaser
from Products.statusmessages.interfaces import IStatusMessage

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


@grok.provider(IContextSourceBinder)
def get_filing_actions(context):

    review_state = context.portal_workflow.getInfoFor(context, 'review_state', None)
    filing_no = getattr(IDossierMarker(context), 'filing_no', None)
    
    values = []
    if review_state != 'dossier-state-resolved':
        if not filing_no:
            values.append(SimpleVocabulary.createTerm(0,_('resolve and set filing no'), _('resolve and set filing no')))
            values.append(SimpleVocabulary.createTerm(1,_('only resolve, set filing no later'), _('only resolve, set filing no later')))
        else:
            values.append(SimpleVocabulary.createTerm(1,_('resolve and take the existing filing no'), _('resolve and take the existing filing no')))
            values.append(SimpleVocabulary.createTerm(0,_('resolve and set a new filing no'), _('resolve and set a new filing no')))
    else:
        if not filing_no:
            values.append(SimpleVocabulary.createTerm(2,_('set a filing no'), _('set a filing no')))
            
    return SimpleVocabulary(values)

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
    
    filing_action = schema.Choice(
        title = _(u'filling_action', default="Action"),
        required = True,
        source = get_filing_actions,
    )

class ArchiveForm(form.Form):
    fields = field.Fields(IArchiveFormSchema)
    ignoreContext = True
    fields['filing_action'].widgetFactory[INPUT_MODE] = radio.RadioFieldWidget
    label = _(u'heading_archive_form', u'Archive Dossier')

    @button.buttonAndHandler(_(u'button_archive', default=u'Archive'))
    def archive(self, action):
        data, errors = self.extractData()
        try:
            action = data['filing_action']
        except KeyError:
            return
        if action == 0 or action == 2:
            if len(errors)>0:
                return
            else:
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

        if action == 0 or action == 1:
            self.request.RESPONSE.redirect(self.context.absolute_url() + '/content_status_modify?workflow_action=dossier-transition-resolve')
        elif action == 2:
            status = IStatusMessage(self.request)
            status.addStatusMessage(_("the filling number was set"), type="info")
            return self.request.RESPONSE.redirect(self.context.absolute_url())
        else:
            status = IStatusMessage(self.request)
            status.addStatusMessage(_("The dossier was already resolved"), type="warning")
            return self.request.RESPONSE.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

class ArchiveFormView(layout.FormWrapper, grok.CodeView):
    grok.context(IDossierMarker)
    grok.name('transition-archive')
    grok.require('zope2.View')
    form = ArchiveForm
    
    #label = _(u'heading_archive_form', u'Archive Dossier')
    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.CodeView.__init__(self, context, request)

    def __call__(self, *args, **kwargs):
        parent = aq_parent(aq_inner(self.context))
        review_state = self.context.portal_workflow.getInfoFor(self.context, 'review_state', None)
        if review_state == 'dossier-state-resolved' and getattr(IDossierMarker(self.context), 'filing_no', None):
            status = IStatusMessage(self.request)
            status.addStatusMessage(_("the filling number was already set"), type="warning")
            self.request.RESPONSE.redirect(self.context.absolute_url())
        if IDossierMarker.providedBy(parent):
            self.request.RESPONSE.redirect(self.context.absolute_url() + '/content_status_modify?workflow_action=dossier-transition-resolve')
        return layout.FormWrapper.__call__(self, *args, **kwargs)
