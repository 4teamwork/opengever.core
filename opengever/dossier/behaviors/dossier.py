from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from OFS.interfaces import IObjectWillBeMovedEvent
from Products.CMFCore.interfaces import ISiteRoot
from collective import dexteritytextindexer
from collective.elephantvocabulary import wrap_vocabulary
from datetime import datetime
from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.base.source import RepositoryPathSourceBinder
from opengever.dossier import _
from opengever.dossier.widget import referenceNumberWidgetFactory
from opengever.mail.interfaces import ISendableDocsContainer
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.ogds.base.interfaces import IContactInformation
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.i18n import MessageFactory as pd_mf
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.directives import form, dexterity
from plone.indexer import indexer
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


class IDossierMarker(Interface, ISendableDocsContainer):
    """ Marker Interface for dossiers.
    """


class IDossier(form.Schema):
    """ Behaviour interface for dossier types providing
    common properties/fields.
    """

    form.fieldset(
        u'common',
        fields=[
            u'keywords',
            u'start',
            u'end',
            u'comments',
            u'responsible',
            u'relatedDossier',
            ],
        )

    dexteritytextindexer.searchable('keywords')
    keywords = schema.Tuple(
        title=_(u'label_keywords', default=u'Keywords'),
        description=_(u'help_keywords', default=u''),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
        )
    form.widget(keywords=TextLinesFieldWidget)

    #workaround because ftw.datepicker wasn't working on the edit form
    form.widget(start=DatePickerFieldWidget)
    start = schema.Date(
        title=_(u'label_start', default=u'Opening Date'),
        description=_(u'help_start', default=u''),
        required=False,
        )

    #workaround because ftw.datepicker wasn't working on the edit form
    form.widget(end=DatePickerFieldWidget)
    end = schema.Date(
        title=_(u'label_end', default=u'Closing Date'),
        description=_(u'help_end', default=u''),
        required=False,
        )

    comments = schema.Text(
        title=_(u'label_comments', default=u'Comments'),
        description=_(u'help_comments', default=u''),
        required=False,
        )

    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description=_(
            u"help_responsible", default="Select the responsible manager"),
        vocabulary=u'opengever.ogds.base.AssignedUsersVocabulary',
        required=True,
        )

    form.fieldset(
        u'filing',
        label=_(u'fieldset_filing', default=u'Filing'),
        fields=[
            u'filing_prefix',
            u'container_type',
            u'number_of_containers',
            u'container_location',
            u'reference_number',
            u'former_reference_number',
            ],
        )

    filing_prefix = schema.Choice(
        title=_(u'filing_prefix', default="filing prefix"),
        source=wrap_vocabulary(
            'opengever.dossier.type_prefixes',
            visible_terms_from_registry="opengever.dossier" + \
                '.interfaces.IDossierContainerTypes.type_prefixes'),
        required=False,
        )

    form.omitted('filing_no')
    filing_no = schema.TextLine(
        title=_(u'filing_no', default="Filing number"),
        description=_(u'help_filing_no', default=u''),
        required=False,
        )

    # needed for temporarily storing current reference number when
    # moving this dossier
    form.omitted('temporary_former_reference_number')
    temporary_former_reference_number = schema.TextLine(
        title=_(u'temporary_former_reference_number',
                default="Temporary former reference number"),
        description=_(u'help_temporary_former_reference_number', default=u''),
        required=False,
        )

    container_type = schema.Choice(
        title=_(u'label_container_type', default=u'Container Type'),
        description=_(u'help_container_type', default=u''),
        source=wrap_vocabulary(
            'opengever.dossier.container_types',
            visible_terms_from_registry="opengever.dossier" + \
                '.interfaces.IDossierContainerTypes.container_types'),
        required=False,
        )

    number_of_containers = schema.Int(
        title=_(u'label_number_of_containers',
                default=u'Number of Containers'),
        description=_(u'help_number_of_containers', default=u''),
        required=False,
        )

    container_location = schema.TextLine(
        title=_(u'label_container_location', default=u'Container Location'),
        description=_(u'help_container_location', default=u''),
        required=False,
        )

    relatedDossier = RelationList(
        title=_(u'label_related_dossier', default=u'Related Dossier'),
        default=[],
        value_type=RelationChoice(
            title=u"Related",
            source=RepositoryPathSourceBinder(
                object_provides='opengever.dossier.behaviors.dossier.' + \
                    'IDossierMarker',
                navigation_tree_query={
                    'object_provides': [
                        'opengever.repository.repositoryroot.IRepositoryRoot',
                        'opengever.repository.repositoryfolder.' + \
                            'IRepositoryFolderSchema',
                        'opengever.dossier.behaviors.dossier.IDossierMarker',
                        ]
                    }),
            ),
        required=False,
        )

    form.mode(former_reference_number='display')
    former_reference_number = schema.TextLine(
        title=_(u'label_former_reference_number',
                  default=u'Reference Number'),
        description=_(u'help_former_reference_number', default=u''),
        required=False,
        )

    form.widget(reference_number=referenceNumberWidgetFactory)
    reference_number = schema.TextLine(
        title=_(u'label_reference_number', default=u'Reference Number'),
        description=_(u'help_reference_number ', default=u''),
        required=False,
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
        """Adds a default value for `responsible` to the request so the
        field is prefilled with the current user, or the parent dossier's
        responsible in the case of a subdossier.
        """
        responsible = getSecurityManager().getUser().getId()
        if IDossierMarker.providedBy(self.context):
            # If adding a subdossier, use parent's responsible
            parent_dossier = IDossier(self.context)
            if parent_dossier:
                responsible = parent_dossier.responsible
        if not self.request.get('form.widgets.IDossier.responsible', None):
            self.request.set('form.widgets.IDossier.responsible',
                             [responsible])
        super(AddForm, self).update()

    @property
    def label(self):
        if IDossierMarker.providedBy(self.context):
            return _(u'Add Subdossier')
        else:
            portal_type = self.portal_type
            fti = getUtility(IDexterityFTI, name=portal_type)
            type_name = fti.Title()
            return pd_mf(u"Add ${name}", mapping={'name': type_name})


class EditForm(dexterity.EditForm):
    """Standard Editform, provide just a special label for subdossiers"""
    grok.context(IDossierMarker)

    @property
    def label(self):
        if IDossierMarker.providedBy(aq_parent(aq_inner(self.context))):
            return _(u'Edit Subdossier')
        else:
            type_name = self.fti.Title()
            return pd_mf(u"Edit ${name}", mapping={'name': type_name})


class StartBeforeEnd(Invalid):
    __doc__ = _(u"The start or end date is invalid")


@form.default_value(field=IDossier['start'])
def deadlineDefaultValue(data):
    return datetime.today()
# TODO: Doesn't work yet


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
    """filing number indexer"""
    dossier = IDossier(obj)
    return getattr(dossier, 'filing_no', None)
grok.global_adapter(filing_no, name="filing_no")


@indexer(IDossierMarker)
def searchable_filing_no(obj):
    """Searchable filing number indexer"""
    dossier = IDossier(obj)
    return getattr(dossier, 'filing_no', None)
grok.global_adapter(searchable_filing_no, name="searchable_filing_no")


@indexer(IDexterityContent)
def containing_subdossier(obj):
    """Returns the title of the subdossier the object is contained in,
    unless it's contained directly in the root of a dossier, in which
    case an empty string is returned.
    """
    context = aq_inner(obj)
    # Only compute for types that actually can be contained in a dossier
    if not context.portal_type in ['opengever.document.document',
                                   'opengever.task.task',
                                   'ftw.mail.mail']:
        return ''

    parent = context
    parent_dossier = None
    parent_dossier_found = False
    while not parent_dossier_found:
        parent = aq_parent(parent)
        if ISiteRoot.providedBy(parent):
            # Shouldn't happen, just to be safe
            break
        if IDossierMarker.providedBy(parent):
            parent_dossier_found = True
            parent_dossier = parent

    if IDossierMarker.providedBy(aq_parent(parent_dossier)):
        # parent dossier is a subdossier
        return parent_dossier.Title()
    return ''
grok.global_adapter(containing_subdossier, name='containing_subdossier')


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
        # responsible
        info = getUtility(IContactInformation)
        dossier = IDossier(self.context)
        searchable.append(info.describe(dossier.responsible).encode(
                'utf-8'))

        # filling_no
        dossier = IDossierMarker(self.context)
        if getattr(dossier, 'filing_no', None):
            searchable.append(str(getattr(dossier, 'filing_no',
                                          None)).encode('utf-8'))

        # comments
        comments = getattr(IDossier(self.context), 'comments', None)
        if comments:
            searchable.append(comments.encode('utf-8'))

        return ' '.join(searchable)


@grok.subscribe(IDossierMarker, IObjectWillBeMovedEvent)
def set_former_reference_before_moving(obj, event):
    """ Temporarily store current reference number before
    moving the dossier.

    """

    # make sure obj wasn't just created or deleted
    if not event.oldParent or not event.newParent:
        return

    repr = IDossier(obj)
    ref_no = getAdapter(obj, IReferenceNumber).get_number()
    IDossier['temporary_former_reference_number'].set(repr, ref_no)


@grok.subscribe(IDossierMarker, IObjectMovedEvent)
def set_former_reference_after_moving(obj, event):
    """ Use the (hopefully) stored former reference number
    as the real new former reference number. This has to
    be done after the dossier was moved.

    """
    # make sure obj wasn't just created or deleted
    if not event.oldParent or not event.newParent:
        return

    repr = IDossier(obj)
    former_ref_no = repr.temporary_former_reference_number
    IDossier['former_reference_number'].set(repr, former_ref_no)
    # reset temporary former reference number
    IDossier['temporary_former_reference_number'].set(repr, '')

    # setting the new number
    parent = aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)
    prefix_adapter.set_number(obj)

    obj.reindexObject(idxs=['reference'])


@grok.subscribe(IDossierMarker, IObjectAddedEvent)
def saveReferenceNumberPrefix(obj, event):
    parent = aq_parent(aq_inner(obj))
    prefix_adapter = IReferenceNumberPrefix(parent)
    if not prefix_adapter.get_number(obj):
        prefix_adapter.set_number(obj)
    obj.reindexObject(idxs=['reference'])
