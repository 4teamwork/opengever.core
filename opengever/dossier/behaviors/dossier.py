import logging

from five import grok
from datetime import datetime
from Acquisition import aq_inner, aq_parent
from opengever.dossier import _
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from zope.app.container.interfaces import IObjectMovedEvent

from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from plone.indexer import indexer
from plone.namedfile.interfaces import INamedFileField
from plone.registry.interfaces import IRegistry
from plone.app.dexterity.behaviors.metadata import IBasic

from zope.interface import invariant, Invalid
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder
from zope import schema
from zope.interface import Interface, alsoProvides
from zope.component import queryUtility, getAdapter, getUtility
from zope.app.container.interfaces import IObjectAddedEvent

from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.dossier.widget import referenceNumberWidgetFactory
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.ogds.base.interfaces import IContactInformation
from opengever.translations.browser.add import TranslatedAddForm

from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

LOG = logging.getLogger('opengever.dossier')


@grok.provider(IContextSourceBinder)
def get_filing_prefixes(context):
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IDossierContainerTypes)
    prefixes = getattr(proxy, 'type_prefixes')
    filing_prefixes = [SimpleTerm(value, value, value) for value in prefixes]

    return SimpleVocabulary(filing_prefixes)


@grok.provider(IContextSourceBinder)
def container_types(context):
    voc= []
    terms = []
    registry = queryUtility(IRegistry)
    proxy = registry.forInterface(IDossierContainerTypes)
    voc = getattr(proxy, 'container_types')
    for term in voc:
        terms.append(SimpleVocabulary.createTerm(term))
    return SimpleVocabulary(terms)


class IDossierMarker(Interface):
    """ Marker Interface for dossiers.
    """


class IDossier(form.Schema):
    """ Behaviour interface for dossier types providing
    common properties/fields.
    """

    form.fieldset(
        u'common',
        fields = [
            u'keywords',
            u'start',
            u'end',
            u'comments',
            u'responsible',
            u'relatedDossier',
            u'former_reference_number',
            ],
        )

    # form.omitted('reference_number_prefix')

    keywords = schema.Tuple(
        title = _(u'label_keywords', default=u'Keywords'),
        description = _(u'help_keywords', default=u''),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )
    form.widget(keywords = TextLinesFieldWidget)


    form.widget(start='ftw.datepicker.widget.DatePickerFieldWidget')
    start = schema.Date(
        title=_(u'label_start', default=u'Opening Date'),
        description = _(u'help_start', default=u''),
        required=False,
        )

    form.widget(end='ftw.datepicker.widget.DatePickerFieldWidget')
    end = schema.Date(
        title=_(u'label_end', default=u'Closing Date'),
        description = _(u'help_end', default=u''),
        required=False,
        )

    volume_number = schema.TextLine(
        title = _(u'label_volume_number', default=u'Volume Number'),
        description = _(u'help_volume_number', default=u''),
        required=False,
        )

    comments = schema.Text(
        title=_(u'label_comments', default=u'Comments'),
        description = _(u'help_comments', default=u''),
        required=False,
        )

    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description =_(
            u"help_responsible", default="select an responsible Manger"),
        #source = util.getManagersVocab,
        vocabulary=u'opengever.ogds.base.AssignedUsersVocabulary',
        required = True,
        )

    form.fieldset(
        u'filing',
        label = _(u'fieldset_filing', default=u'Filing'),
        fields = [
            u'filing_prefix',
            u'container_type',
            u'container_id',
            u'volume_number',
            u'number_of_containers',
            u'container_location',
            u'reference_number',
            u'former_reference_number',
            ],
        )

    filing_prefix = schema.Choice(
        title = _(u'filing_prefix', default="filing prefix"),
        source = get_filing_prefixes,
        required = False,
    )

    container_type = schema.Choice(
        title = _(u'label_container_type', default=u'Container Type'),
        description = _(u'help_container_type', default=u''),
        source = container_types,
        required = False,
        )

    container_id = schema.TextLine(
        title = _(u'label_container_id', default=u'Container Id'),
        description = _(u'help_container_id', default=u''),
        required = False,
        )

    number_of_containers = schema.Int(
        title = _(
            u'label_number_of_containers',
            default=u'Number of Containers'),
        description = _(u'help_number_of_containers', default=u''),
        required = False,
        )

    container_location = schema.TextLine(
        title = _(u'label_container_location', default=u'Container Location'),
        description = _(u'help_container_location', default=u''),
        required = False,
        )

    relatedDossier = RelationList(
        title=_(u'label_related_dossier', default=u'Related Dossier'),
        default=[],
        value_type=RelationChoice(title=u"Related",
            source=ObjPathSourceBinder(
                portal_type="opengever.dossier.businesscasedossier", ),
        ),
        required=False,
        )

    form.mode(former_reference_number='display')
    former_reference_number = schema.TextLine(
        title = _(u'label_former_reference_number',
            default=u'Reference Number'),
        description = _(u'help_former_reference_number', default=u''),
        required = False,
        )

    form.widget(reference_number=referenceNumberWidgetFactory)
    reference_number= schema.TextLine(
        title = _(u'label_reference_number', default=u'Reference Number'),
        description = _(u'help_reference_number ', default=u''),
        required = False,
        )

    @invariant
    def validateStartEnd(data):
        if data.start is not None and data.end is not None:
            if data.start > data.end:
                raise StartBeforeEnd(
                    _(u"The start date must be before the end date."))

alsoProvides(IDossier, IFormFieldProvider)


# TODO: temporary default value (autocompletewidget)
class AddForm(TranslatedAddForm):
    grok.name('opengever.dossier.businesscasedossier')

    def update(self):
        """adds responsible to the request"""
        responsible = ''
        if self.context.portal_type == 'opengever.dossier.businesscasedossier':
            tmp_dossier = IDossier(self.context)
            if tmp_dossier:
                responsible = tmp_dossier.responsible
        responsible = responsible and responsible or ''
        if not self.request.get('form.widgets.IDossier.responsible', None):
            self.request.set('form.widgets.IDossier.responsible', [responsible])
        super(AddForm, self).update()


class StartBeforeEnd(Invalid):
    __doc__ = _(u"The start or end date is invalid")


@form.default_value(field=IDossier['start'])
def deadlineDefaultValue(data):
    return datetime.today()
# TODO: Doesn't work yet


#@form.default_value(field=IDossier['responsible'])
def responsibleDefaultValue(data):
    if data.context.portal_type == 'opengever.dossier.businesscasedossier':
        tmp_dossier = IDossier(data.context)
        if tmp_dossier:
            return tmp_dossier.responsible
    return ''


@indexer(IDossierMarker)
def startIndexer(obj):
    aobj = IDossier(obj)
    if aobj.start is None:
        return None
    return aobj.start
grok.global_adapter(startIndexer, name="start")


@indexer(IDossierMarker)
def endIndexer(obj):
    aobj = IDossier(obj)
    if aobj.end is None:
        return None
    return aobj.end
grok.global_adapter(endIndexer, name="end")


@indexer(IDossierMarker)
def responsibleIndexer(obj):
    aobj = IDossier(obj)
    if aobj.responsible is None:
        return None
    return aobj.responsible
grok.global_adapter(responsibleIndexer, name="responsible")


@indexer(IDossierMarker)
def isSubdossierIndexer(obj):
    parent = aq_parent(aq_inner(obj))
    if IDossierMarker.providedBy(parent):
        return True
    return False
grok.global_adapter(isSubdossierIndexer, name="is_subdossier")


@indexer(IDossierMarker)
def filing_no(obj):
    """filing nubmer indexer"""

    return getattr(obj, 'filing_no', None)
grok.global_adapter(filing_no, name="filing_no")


@indexer(IDossierMarker)
def SearchableText(obj):
    """searchableText indexer"""
    context = aq_inner(obj)
    transforms = getToolByName(obj, 'portal_transforms')
    fields = [
        schema.getFields(IBasic).get('title'),
        schema.getFields(IBasic).get('description'),
        schema.getFields(IDossier).get('keywords'),
        ]
    searchable = []
    for field in fields:
        try:
            data = field.get(context)
        except AttributeError:
            data = field.get(field.interface(context))
        if not data:
            continue
        if INamedFileField.providedBy(field):
            # we need to convert the file data to string, so we can
            # index it
            datastream = ''
            try:
                datastream = transforms.convertTo(
                    "text/plain",
                    data.data,
                    mimetype = data.contentType,
                    filename = data.filename,
                    )
            except (ConflictError, KeyboardInterrupt):
                raise
            except Exception, e:
                LOG.error("Error while trying to convert file contents "
                          "to 'text/plain' "
                          "in SearchablceIndex(dossier.py): %s" % (e, ))
            data = str(datastream)
        if isinstance(data, tuple) or isinstance(data, list):
            data = " ".join([isinstance(a, unicode) and a.encode('utf-8') or a for a in data])
        if data:
            searchable.append(data)
    # append some other attributes to the searchableText index
    # reference_number
    refNumb = getAdapter(obj, IReferenceNumber)
    searchable.append(refNumb.get_number())

    # sequence_number
    seqNumb = getUtility(ISequenceNumber)
    searchable.append(str(seqNumb.get_number(obj)))

    #responsible
    info = getUtility(IContactInformation)
    dossier = IDossier(obj)
    searchable.append(info.describe(dossier.responsible))

    #filling_no
    dossier = IDossierMarker(obj)
    if getattr(dossier, 'filing_no', None):
        searchable.append(str(getattr(dossier, 'filing_no', None)))
    return ' '.join(searchable).encode('utf-8')

grok.global_adapter(SearchableText, name='SearchableText')


@grok.subscribe(IDossierMarker, IObjectMovedEvent)
def set_former_reference_after_moving(obj, event):
    if not event.oldParent or not event.newParent:
        # object was just created or deleted
        return
    # we need to reconstruct the reference number
    new_obj_rn = getAdapter(obj, IReferenceNumber).get_number()
    new_par_rn = getAdapter(event.newParent, IReferenceNumber).get_number()
    old_par_rn = getAdapter(event.oldParent, IReferenceNumber).get_number()
    old_obj_rn = old_par_rn + new_obj_rn[len(new_par_rn):]
    repr = IDossier(obj)
    IDossier['former_reference_number'].set(repr, old_obj_rn)

    from z3c.form.interfaces import IValue
    from zope.component import queryMultiAdapter

    default = queryMultiAdapter((
        obj,
        obj.REQUEST, # request
        None, # form
        IReferenceNumber.get('reference_number'),
        None, # Widget
        ), IValue, name='default')
    if default!=None:
        default = default.get()
        IReferenceNumber.get('reference_number').set(
            IReferenceNumber(obj), default)


@grok.subscribe(IDossierMarker, IObjectAddedEvent)
def saveReferenceNumberPrefix(obj, event):
    parent= aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)
    if not prefix_adapter.get_number(obj):
        prefix_adapter.set_number(obj)
