from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from collective import dexteritytextindexer
from collective.elephantvocabulary import wrap_vocabulary
from datetime import datetime
from five import grok
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.dossier import _
from opengever.dossier.widget import referenceNumberWidgetFactory
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.ogds.base.interfaces import IContactInformation
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form, dexterity
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer import indexer
from plone.namedfile.interfaces import INamedFileField
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectMovedEvent
from zope.component import getAdapter, getUtility
from zope.interface import Interface, alsoProvides
from zope.interface import invariant, Invalid
import logging


LOG = logging.getLogger('opengever.dossier')


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
            ],
        )

    # form.omitted('reference_number_prefix')

    dexteritytextindexer.searchable('keywords')
    keywords = schema.Tuple(
        title = _(u'label_keywords', default=u'Keywords'),
        description = _(u'help_keywords', default=u''),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )
    form.widget(keywords = TextLinesFieldWidget)


    start = schema.Date(
        title=_(u'label_start', default=u'Opening Date'),
        description = _(u'help_start', default=u''),
        required=False,
        )

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
            u"help_responsible", default="Select the responsible manager"),
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
        source = wrap_vocabulary('opengever.dossier.type_prefixes',
                    visible_terms_from_registry="opengever.dossier" + \
                        '.interfaces.IDossierContainerTypes.type_prefixes'),
        required = False,
    )

    container_type = schema.Choice(
        title = _(u'label_container_type', default=u'Container Type'),
        description = _(u'help_container_type', default=u''),
        source = wrap_vocabulary('opengever.dossier.type_prefixes',
                    visible_terms_from_registry="opengever.dossier" + \
                        '.interfaces.IDossierContainerTypes.container_types'),
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
class AddForm(dexterity.AddForm):
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


class SearchableTextExtender(grok.Adapter):
    grok.context(IDossierMarker)
    grok.name('IDossier')
    grok.implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable = []
        # append some other attributes to the searchableText index
        # reference_number
        refNumb = getAdapter(self.context, IReferenceNumber)
        searchable.append(refNumb.get_number())

        # sequence_number
        seqNumb = getUtility(ISequenceNumber)
        searchable.append(str(seqNumb.get_number(self.context)))

        #responsible
        info = getUtility(IContactInformation)
        dossier = IDossier(self.context)
        searchable.append(info.describe(dossier.responsible).encode(
                'utf-8'))

        #filling_no
        dossier = IDossierMarker(self.context)
        if getattr(dossier, 'filing_no', None):
            searchable.append(str(getattr(dossier, 'filing_no',
                                      None)).encode('utf-8'))

        return ' '.join(searchable)


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

    # setting the new number
    parent= aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)
    prefix_adapter.set_number(obj)

    obj.reindexObject(idxs=['reference'])

@grok.subscribe(IDossierMarker, IObjectAddedEvent)
def saveReferenceNumberPrefix(obj, event):
    parent= aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)
    if not prefix_adapter.get_number(obj):
        prefix_adapter.set_number(obj)
    obj.reindexObject(idxs=['reference'])
