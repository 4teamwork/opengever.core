

import logging

from Acquisition import aq_inner
from ZODB.POSException import ConflictError
from five import grok
from z3c.form.browser import checkbox
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from zope.component import queryUtility, getUtility, getAdapter
from zc.relation.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds
from datetime import datetime

from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from Products.ARFilePreview.interfaces import IPreviewable
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.dexterity.content import Item
from plone.directives import form, dexterity
from plone.indexer import indexer
from plone.app.iterate.interfaces import IWorkingCopy
from plone.stagingbehavior.relation import StagingRelationValue
from plone.registry.interfaces import IRegistry
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.app.layout.viewlets.interfaces import IBelowContentBody
from plone.autoform.interfaces import ORDER_KEY
from plone.autoform.interfaces import OMITTED_KEY
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from plone.versioningbehavior.behaviors import IVersionable
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from plone.i18n.normalizer.interfaces import IIDNormalizer

from zope.annotation.interfaces import IAnnotations
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectModifiedEvent

from ftw.table.interfaces import ITableGenerator
from ftw.table import helper

from opengever.sqlfile.field import NamedFile
from plone.namedfile.interfaces import INamedFileField

from opengever.document import _
from opengever.document.interfaces import IDocumentType
from ftw.journal.interfaces import IAnnotationsJournalizable, IWorkflowHistoryJournalizable

from plone.memoize.instance import memoize
from plone.app.layout.viewlets import content
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from zope.annotation.interfaces import IAnnotations, IAnnotatable

from plone.directives.dexterity import DisplayForm

from opengever.tabbedview.browser.tabs import OpengeverTab, OpengeverListingTab, OpengeverSolrListingTab
from opengever.tabbedview.helper import readable_ogds_author, linked
from opengever.tabbedview import _ as tvmf
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.octopus.tentacle.interfaces import IContactInformation

from ftw.task import _ as taskmsg

LOG = logging.getLogger('opengever.document')

IVersionable.setTaggedValue( FIELDSETS_KEY, [
        Fieldset( 'common', fields=[
                'changeNote',
                ])
        ] )
IVersionable.setTaggedValue( OMITTED_KEY, {
        'changeNote' : 'true',
        } )

@grok.provider(IContextSourceBinder)
def possibleTypes(context):
    voc= []
    terms = []
    registry = queryUtility(IRegistry)
    proxy = registry.forInterface(IDocumentType)
    voc = getattr(proxy, 'document_types')
    for term in voc:
        terms.append(SimpleVocabulary.createTerm(term))
    return SimpleVocabulary(terms)
    
def related_document(context):
    intids = getUtility( IIntIds )
    return intids.getId( context )

class IDocumentSchema(form.Schema):
    """ Document Schema Interface
    """

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', u'Dates'),
        fields = [
            u'title',
            u'description',
            u'keywords',
            u'foreign_reference',
            u'document_date',
            u'receipt_date',
            u'delivery_date',
            u'document_type',
            u'document_author',
            u'file',
            u'paper_form',
            u'preserved_as_paper',
            u'archival_file',
            u'thumbnail',
            ]
        )

    title = schema.TextLine(
        title = _(u'label_title', default=u'Title'),
        required = True
        )

    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        description = _(u'help_description', default=u''),
        required = False,
        )

    keywords = schema.Tuple(
        title = _(u'label_keywords', default=u'Keywords'),
        description = _(u'help_keywords', default=u''),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )
    form.widget(keywords = TextLinesFieldWidget)

    foreign_reference = schema.TextLine(
        title = _(u'label_foreign_reference', default='Foreign Reference'),
        description = _('help_foreign_reference', default=''),
        required = False,
        )

    form.widget(document_date='ftw.datepicker.widget.DatePickerFieldWidget')
    document_date = schema.Date(
        title = _(u'label_document_date', default='Document Date'),
        description = _(u'help_document_date', default=''),
        required = True,
        )

    document_type = schema.Choice(
        title=_(u'label_document_type', default='Document Type'),
        description=_(u'help_document_type', default=''),
        source=possibleTypes,
        required = False,
        )

    document_author = schema.TextLine(
        title=_(u'label_author', default='Author'),
        description=_(u'help_author', default=""),
        required=False,
        )

    form.primary('file')
    file = NamedFile(
        title = _(u'label_file', default='File'),
        description = _(u'help_file', default=''),
        required = False,
        )

    form.widget(paper_form=checkbox.SingleCheckBoxFieldWidget)
    paper_form = schema.Bool(
        title = _(u'label_paper_form', default='Paper form'),
        description = _(u'help_paper_form', default='Available in paper form only'),
        required = False,
        )

    form.widget(preserved_as_paper=checkbox.SingleCheckBoxFieldWidget)
    preserved_as_paper = schema.Bool(
        title = _(u'label_preserved_as_paper', default='Preserved as paper'),
        description = _(u'help_preserved_as_paper', default=''),
        required = False,
        default = True,
        )

    form.omitted('archival_file')
    archival_file = NamedFile(
        title = _(u'label_archival_file', default='Archival File'),
        description = _(u'help_archival_file', default=''),
        required = False,
        )

    form.omitted('thumbnail')
    thumbnail = NamedFile(
        title = _(u'label_thumbnail', default='Thumbnail'),
        description = _(u'help_thumbnail', default=''),
        required = False,
        )

    form.omitted('preview')
    preview = NamedFile(
        title = _(u'label_preview', default='Preview'),
        description = _(u'help_preview', default=''),
        required = False,
        )

    form.widget(receipt_date='ftw.datepicker.widget.DatePickerFieldWidget')
    receipt_date = schema.Date(
        title = _(u'label_receipt_date', default='Date of receipt'),
        description = _(u'help_receipt_date', default=''),
        required = False,
        )

    form.widget(delivery_date='ftw.datepicker.widget.DatePickerFieldWidget')
    delivery_date = schema.Date(
        title = _(u'label_delivery_date', default='Date of delivery'),
        description = _(u'help_delivery_date', default=''),
        required = False,
        )

    form.order_after(**{'IRelatedItems.relatedItems': 'file'})

@form.default_value(field=IDocumentSchema['document_date'])
def docuementDateDefaulValue(data):
    return datetime.today()

@form.default_value(field=IDocumentSchema['document_author'])
def deadlineDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    user = data.context.portal_membership.getAuthenticatedMember()
    if user.getProperty('fullname'):
        return user.getProperty('fullname').decode('utf8')
    else:
        return user.getId()

class Document(Item):

    # disable file preview creation when modifying or creating document
    buildPreview = False

    def Title(self):
        title = Item.Title(self)
        if IWorkingCopy.providedBy(self):
            return '%s (WorkingCopy)' % title
        return title

    def getIcon(self, relative_to_portal=0):
        """Calculate the icon using the mime type of the file
        """
        surrender = lambda :super(Document, self).getIcon(relative_to_portal=relative_to_portal)
        mtr   = getToolByName(self, 'mimetypes_registry', None)
        utool = getToolByName(self, 'portal_url')

        field = self.file
        if not field or not field.getSize():
            # there is no file
            return surrender()

        # get icon by content type
        contenttype       = field.contentType
        contenttype_major = contenttype and contenttype.split('/')[0] or ''
        mimetypeitem = None
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException, msg:
            LOG.error('MimeTypeException for %s. Error is: %s' % (self.absolute_url(), str(msg)))
        if not mimetypeitem:
            # not found
            return surrender()
        icon = mimetypeitem[0].icon_path

        if relative_to_portal:
            return icon
        else:
            # Relative to REQUEST['BASEPATH1']
            res = utool(relative=1) + '/' + icon
            while res[:1] == '/':
                res = res[1:]
            return res

    def icon(self):
        """for ZMI
        """
        return self.getIcon()



@indexer(IDocumentSchema)
def related_items( obj ):
    catalog = getUtility( ICatalog )
    intids = getUtility( IIntIds )
    obj_id = intids.getId( obj )
    results = []
    relations = catalog.findRelations({'to_id' : obj_id, 'from_attribute': 'relatedItems'})
    for rel in relations:
        results.append(rel.from_id)
    return results
    
    
grok.global_adapter(related_items, name='related_items')


# INDEX: SearchableText
@indexer(IDocumentSchema)
def SearchableText( obj ):
    context = aq_inner( obj )
    transforms = getToolByName(obj, 'portal_transforms')
    fields = [
        schema.getFields( IBasic ).get( 'title' ),
        schema.getFields( IBasic ).get( 'description' ),
        schema.getFields( IDocumentSchema).get('keywords'),
        schema.getFields( IDocumentSchema ).get('file'),
        ]
    searchable = []
    
    #Reference Number
    ref_number = IReferenceNumber(obj).get_number()
    searchable.append(ref_number)
    #Sequence Number
    seq_number = str(getUtility(ISequenceNumber).get_number(obj))
    searchable.append(seq_number)
    
    for field in fields:
        data = field.get( context )
        if not data:
            continue
        if INamedFileField.providedBy( field ):
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
                LOG.error("Error while trying to convert file contents to 'text/plain' "
                          "in SearchableIndex(document.py): %s" % (e,))
            data = str(datastream)
        if isinstance(data, unicode):
            data = data.encode('utf8')
        if isinstance(data, tuple) or isinstance(data, list):
            data = " ".join([str(a) for a in data])
        if data:
            searchable.append(data)
    return ' '.join(searchable)
    
grok.global_adapter(SearchableText, name='SearchableText')


# INDEX: document_author
@indexer( IDocumentSchema )
def document_author( obj ):
    context = aq_inner( obj )
    if not context.document_author:
        return None
    return context.document_author
grok.global_adapter( document_author, name='document_author' )


# INDEX: document_date
@indexer( IDocumentSchema )
def document_date( obj ):
    context = aq_inner( obj )
    if not context.document_date:
        return None
    return context.document_date
grok.global_adapter( document_date, name='document_date' )


# INDEX: receipt_date
@indexer( IDocumentSchema )
def receipt_date( obj ):
    context = aq_inner( obj )
    if not context.receipt_date:
        return None
    return context.receipt_date
grok.global_adapter( receipt_date, name='receipt_date' )


# INDEX: delivery_date
@indexer( IDocumentSchema )
def delivery_date( obj ):
    context = aq_inner( obj )
    if not context.delivery_date:
        return None
    return context.delivery_date
grok.global_adapter( delivery_date, name='delivery_date' )

# INDEX: checked_out
@indexer( IDocumentSchema )
def checked_out( obj ):
    context = aq_inner( obj )
    rels = StagingRelationValue.get_relations_of( context )
    if len( rels ):
        rel = rels[0]
        return rel.creator
    return '-'
grok.global_adapter( checked_out, name='checked_out' )

@grok.subscribe(IDocumentSchema, IObjectCreatedEvent)
def setID(document, event):
    document.id = "document-%s" % getUtility(ISequenceNumber).get_number(document)

@grok.subscribe(IDocumentSchema, IObjectCreatedEvent)
def setImageName(document, event):
    if document.file:
        filename = document.file.filename
        normalize = getUtility(IIDNormalizer).normalize
        document.file.filename = normalize(document.title) + filename[filename.rfind('.'):]


@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def checkImageName(document, event):
    if document.file:
        if document.file.filename[:document.file.filename.rfind('.')] != document.title:
            setImageName(document, event)


class View(dexterity.DisplayForm):
    grok.context(IDocumentSchema)
    grok.require("zope2.View")

    def creator_link(self):
        info = getUtility(IContactInformation)
        return info.render_link(self.context.Creator())
        
class ForwardViewlet(grok.Viewlet):
    """Display the message subject
    """
    grok.name('opengever.document.ForwardViewlet')
    grok.context(IDocumentSchema)
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContentTitle)

    def render(self):
        if self.request.get("externaledit",None):
            return '<script language="JavaScript">jq(function(){window.location.href="'+str(self.context.absolute_url())+'/external_edit"})</script>'
        return ''

class Byline(grok.Viewlet, content.DocumentBylineViewlet):
    grok.viewletmanager(IBelowContentTitle)
    grok.context(IDocumentSchema)
    grok.name("plone.belowcontenttitle.documentbyline")

    update = content.DocumentBylineViewlet.update

    def responsible(self):
        mt=getToolByName(self.context,'portal_membership')
        document = IDocumentSchema(self.context)
        return mt.getMemberById(document.responsible)

    @memoize
    def workflow_state(self):
        state = self.context_state.workflow_state()
        workflows = self.tools.workflow().getWorkflowsFor(self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state

    @memoize
    def sequence_number(self):
        seqNumb = getUtility(ISequenceNumber)
        return seqNumb.get_number(self.context)

    @memoize
    def reference_number(self):
        refNumb = getAdapter(self.context, IReferenceNumber)
        return refNumb.get_number()


class Overview(DisplayForm, OpengeverTab):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def get_referenced_documents(self):
        pc = self.context.portal_catalog
        return pc({'portal_type':'Document',})

    def creator_link(self):
        info = getUtility(IContactInformation)
        return info.render_link(self.context.Creator())


class Preview(DisplayForm, OpengeverTab):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-preview')
    grok.template('preview')

    def __call__(self):
        IPreviewable(self.context).buildAndStorePreview()
        return DisplayForm.__call__(self)
        
#XXX TEMPORARY REPLACED WITH A NON SOLR TAB
#class Tasks(OpengeverSolrListingTab):
#     grok.context(IDocumentSchema)
#     grok.name('tabbedview_view-tasks')
#     grok.template('generic')
#     columns= (
#         ('', helper.draggable),
#         ('', helper.path_checkbox),
#         ('Title', helper.solr_linked),
#         ('deadline', helper.readable_date),
#         'responsible',
#         ('review_state', 'review_state', helper.translated_string()),
#         )
#         
#     def build_query(self):
#         intids = getUtility( IIntIds )
#         obj_id = intids.getId( self.context )
#         return 'portal_type:ftw.task.task AND related_items:%s' % obj_id


class Tasks(OpengeverListingTab):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-tasks')
    grok.template('generic')
    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', 'sortable_title', linked),
        {'column' : 'task_type', 
        'column_title' : taskmsg(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        ('date_of_completion', helper.readable_date), # erledigt am
        {'column' : 'responsible', 
        'column_title' : taskmsg(u'label_responsible_task', 'Responsible'),  
        'transform' : readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column' : 'created', 
        'column_title' : taskmsg(u'label_issued_date', 'issued at'),
        'transform': helper.readable_date },
        )

    types = ['ftw.task.task', ]

    search_options = {'related_items': related_document}

    def search(self, kwargs):
        catalog = getToolByName(self.context,'portal_catalog')
        self.contents = catalog(**kwargs)
        self.len_results = len(self.contents)


class Journal(grok.View, OpengeverTab):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-journal')
    grok.template('journal')
    def table(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        columns = (('title', lambda x,y: x['action']['title']),
                   'actor',
                   ('time', helper.readable_date_time),
                   'comment'
                   )
        return generator.generate(reversed(self.data()), columns, css_mapping={'table':'journal-listing'})

    def data(self):
        context = self.context
        history = []

        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(context)
            return annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
        elif IWorkflowHistoryJournalizable.providedBy(self.context):
            raise NotImplemented


class DocumentContentHistoryViewlet(grok.Viewlet,
                                     content.ContentHistoryViewlet):
    """ Custom version of content history viewlet for documents
    """
    grok.name('plone.belowcontentbody.contenthistory')
    grok.context(IDocumentSchema)
    grok.viewletmanager(IBelowContentBody)
    grok.require('zope2.View')

    update = content.ContentHistoryViewlet.update

 
class DownloadFileVersion(grok.CodeView):
    grok.context(IDocumentSchema)
    grok.name('download_file_version')

    def render(self):
        version_id = self.request.get('version_id')
        pr = self.context.portal_repository
        old_obj = pr.retrieve(self.context, version_id).object
        old_file = old_obj.file
        response = self.request.RESPONSE
        response.setHeader('Content-Type', old_file.contentType)
        response.setHeader('Content-Length', old_file.getSize())
        response.setHeader('Content-Disposition',
                           'attachment;filename="%s"' % old_file.filename)
        return old_file.data

class Byline(grok.Viewlet, content.DocumentBylineViewlet):
    grok.viewletmanager(IBelowContentTitle)
    grok.context(IDocumentSchema)
    grok.name("plone.belowcontenttitle.documentbyline")

    update = content.DocumentBylineViewlet.update

    def start(self):
        document = IDocumentSchema(self.context)
        return document.start

    def responsible(self):
        mt=getToolByName(self.context,'portal_membership')
        document = IDocumentSchema(self.context)
        return mt.getMemberById(document.responsible)

    def end(self):
        document = IDocumentSchema(self.context)
        return document.end

    @memoize
    def workflow_state(self):
        state = self.context_state.workflow_state()
        workflows = self.tools.workflow().getWorkflowsFor(self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state

    @memoize
    def sequence_number(self):
        seqNumb = getUtility(ISequenceNumber)
        return seqNumb.get_number(self.context)

    @memoize
    def reference_number(self):
        refNumb = getAdapter(self.context, IReferenceNumber)
        return refNumb.get_number()

    def get_filing_no(self):
        document = IDocumentSchema(self.context)
        return getattr(document, 'filing_no', None)

    # TODO: should be more generic ;-)
    #       use sequence_number instead of intid
    def email(self):
        if IMailInAddressMarker.providedBy(self.context):
            return IMailInAddress(self.context).get_email_address()

