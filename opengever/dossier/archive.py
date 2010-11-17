from Acquisition import aq_inner, aq_parent
from collective.elephantvocabulary import wrap_vocabulary
from datetime import datetime, time
from five import grok
from ftw.table.catalog_source import default_custom_sort
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.interfaces import IBaseClientID
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from persistent.dict import PersistentDict
from plone.directives import form as directives_form
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from Products.Transience.Transience import Increaser
from z3c.form import button, field
from z3c.form import validator
from z3c.form.browser import radio
from z3c.form.interfaces import INPUT_MODE
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility, provideAdapter
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


class MissingValue(Invalid):
    """ The Missing value was defined Exception."""
    __doc__ = _(u"Not all required fields are filled")


class EnddateValidator(validator.SimpleFieldValidator):
    """check if the subdossier hasn't a younger date,
    than the given enddate"""

    def validate(self, value):
        if not value:
            raise MissingValue(_(u'error_enddate', default=u'The enddate is required.'))
            
        subdossiers = self.context.portal_catalog(
            path=dict(
                query='/'.join(self.context.getPhysicalPath()),
                depth=-1) ,
            object_provides= 'opengever.dossier.behaviors.dossier.IDossierMarker'
        )
        if len(subdossiers) != 0:
            subdossiers = default_custom_sort(subdossiers, 'end', True)
            if subdossiers[0].end:
                sub_end = datetime.combine(subdossiers[0].end, time(0,0))
                if sub_end and datetime.combine(value, time(0,0)) < sub_end:
                    raise Invalid(
                        _(u'The given end date is older than the end date \
                            of the youngest subdossier(${number})',
                                mapping = {'number':subdossiers[0].end}))



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

class IArchiveFormSchema(directives_form.Schema):

    filing_prefix = schema.Choice(
        title = _(u'filing_prefix', default="filing prefix"),
        source = wrap_vocabulary('opengever.dossier.type_prefixes',
                    visible_terms_from_registry="opengever.dossier" + \
                        ".interfaces.IDossierContainerTypes.type_prefixes"),
        required=False,
    )

    dossier_enddate = schema.Date(
        title=_(u'label_end', default=u'Closing Date'),
        description = _(u'help_end', default=u''),
        required=True,
    )

    filing_year = schema.TextLine(
        title = _(u'filing_year', default="filing Year"),
        required=False,
    )

    filing_action = schema.Choice(
        title = _(u'filing_action', default="Action"),
        source = get_filing_actions,
        required = True,
    )

    @invariant
    def validateStartEnd(data):
        if (data.filing_action == 0 or data.filing_action == 2) and \
            (data.filing_prefix is None or data.filing_year is None):
            raise Invalid(
                _(u"When the Action give filing number is selected, \
                    all fields are required."))


@directives_form.default_value(field=IArchiveFormSchema['filing_prefix'])
def filing_prefix_default_value(data):
    prefix = IDossier(data.context).filing_prefix
    if prefix:
        return prefix.decode('utf-8')
    return ""

@directives_form.default_value(field=IArchiveFormSchema['filing_year'])
def filing_year_default_value(data):
    documents = data.context.portal_catalog(
        path=dict(
            query='/'.join(data.context.getPhysicalPath()),
            depth=-1) ,
        portal_type= ['opengever.document.document'],
    )
    if len(documents) == 0:
        return None
    else:
        documents = default_custom_sort(documents, 'document_date', True)
        return str(documents[0].getObject().document_date.year)

@directives_form.default_value(field=IArchiveFormSchema['dossier_enddate'])
def dossier_date_default_value(data):
    dossier_end = IDossier(data.context).end
    documents = data.context.portal_catalog(
        path=dict(
            query='/'.join(data.context.getPhysicalPath()),
        ),
        portal_type= ['opengever.document.document'],
    )
    if len(documents) != 0:
        documents = default_custom_sort(documents, 'document_date', True)
        if dossier_end == None or dossier_end < documents[0].document_date:
            return documents[0].document_date
    return dossier_end


class ArchiveForm(directives_form.Form):
    grok.context(IDossierMarker)
    grok.name('transition-archive')
    grok.require('zope2.View')

    fields = field.Fields(IArchiveFormSchema)
    ignoreContext = True
    fields['filing_action'].widgetFactory[INPUT_MODE] = radio.RadioFieldWidget
    fields['dossier_enddate'].widgetFactory[INPUT_MODE] = DatePickerFieldWidget
    label = _(u'heading_archive_form', u'Archive Dossier')

    def __call__(self):
        """ check if the filing number already exist,
        and redirect to the workflow_action if the context are a subdossier
        """
        parent = aq_parent(aq_inner(self.context))
        review_state = self.context.portal_workflow.getInfoFor(
            self.context, 'review_state', None)

        if review_state == 'dossier-state-resolved' and \
                getattr(IDossierMarker(self.context), 'filing_no', None):
            status = IStatusMessage(self.request)
            status.addStatusMessage(
                _("the filling number was already set"),
                 type="warning")
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        if IDossierMarker.providedBy(parent):
            return self.request.RESPONSE.redirect(
                self.context.absolute_url() + \
                '/content_status_modify?workflow_action=dossier-transition-resolve')
        return super(ArchiveForm, self).__call__()

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

                filing_year = data.get('filing_year')
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

                # set the dossier end date and the dossier filing prefix
                IDossier(self.context).end = data.get('dossier_enddate')
                IDossier(self.context).filing_prefix = data.get('filing_prefix')

                # create filing number for all subdossiers
                # and resolve them also
                subdossiers = self.context.portal_catalog(
                    portal_type="opengever.dossier.businesscasedossier",
                    path=dict(depth=1,
                        query='/'.join(self.context.getPhysicalPath()),
                    ),
                    sort_on='filing_no',
                )

                counter = 1
                wft = self.context.portal_workflow
                for dossier in subdossiers:

                    dossier = dossier.getObject()
                    dossier.filing_no = filing_no + "." + str(counter)
                    counter += 1
                    wft.doActionFor(dossier, 'dossier-transition-resolve')

        if action == 0 or action == 1:
            data, errors = self.extractData()
            if data.get('dossier_enddate') == None:
                status = IStatusMessage(self.request)
                status.addStatusMessage(_("The End that is required, also if only closing is selected"), type="error")
                return
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

validator.WidgetValidatorDiscriminators(
    EnddateValidator,
    field=IArchiveFormSchema['dossier_enddate'],
)

provideAdapter(EnddateValidator)

