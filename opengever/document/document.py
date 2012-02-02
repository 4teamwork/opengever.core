from Acquisition import aq_inner, aq_base
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from collective import dexteritytextindexer
from collective.elephantvocabulary import wrap_vocabulary
from datetime import date
from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.document import _
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.tabbedview.browser.tabs import Tasks
from opengever.tabbedview.helper import readable_ogds_author
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.app.versioningbehavior.behaviors import IVersionable
from plone.autoform.interfaces import OMITTED_KEY
from plone.dexterity.content import Item
from plone.directives import form, dexterity
from plone.directives.dexterity import DisplayForm
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.indexer import indexer
from plone.namedfile.field import NamedBlobFile
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.form.browser import checkbox
from zc.relation.interfaces import ICatalog
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, queryMultiAdapter, getAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import invariant, Invalid, Interface
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import logging


LOG = logging.getLogger('opengever.document')

# move and omit the changeNote,
# because it's not possible to make a new version when you editing a file
IVersionable.setTaggedValue(FIELDSETS_KEY, [
        Fieldset('common', fields=[
                'changeNote',
                ])
        ])

# TODO: Not Work in plone 4 and the dexterity b2 release
# possibly it can be solved with plone.directives
IVersionable.setTaggedValue(OMITTED_KEY,
    [(Interface, 'changeNote', 'true'), ])


def related_document(context):
    intids = getUtility(IIntIds)
    return intids.getId(context)


class IDocumentSchema(form.Schema):
    """ Document Schema Interface
    """

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', u'Common'),
        fields=[
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
            u'digitally_available',
            u'preserved_as_paper',
            u'archival_file',
            u'thumbnail',
            ],
        )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        description=_(u'help_description', default=u''),
        required=False,
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

    foreign_reference = schema.TextLine(
        title=_(u'label_foreign_reference', default='Foreign Reference'),
        description=_('help_foreign_reference', default=''),
        required=False,
        )

    document_date = schema.Date(
        title=_(u'label_document_date', default='Document Date'),
        description=_(u'help_document_date', default=''),
        required=False,
        )

    #workaround because ftw.datepicker wasn't working
    form.widget(document_date=DatePickerFieldWidget)

    document_type = schema.Choice(
        title=_(u'label_document_type', default='Document Type'),
        description=_(u'help_document_type', default=''),
        source=wrap_vocabulary('opengever.document.document_types',
                    visible_terms_from_registry='opengever.document' + \
                            '.interfaces.IDocumentType.document_types'),
        required=False,
        )

    dexteritytextindexer.searchable('document_author')
    document_author = schema.TextLine(
        title=_(u'label_author', default='Author'),
        description=_(u'help_author', default=""),
        required=False,
        )

#    dexteritytextindexer.searchable('file')
    form.primary('file')
    file = NamedBlobFile(
        title=_(u'label_file', default='File'),
        description=_(u'help_file', default=''),
        required=False,
        )

    form.mode(digitally_available='hidden')
    digitally_available = schema.Bool(
        title=_(u'label_digitally_available', default='Digital Available'),
        description=_(u'help_digitally_available',
            default='Is the Document Digital Availabe'),
        required=False,
        )

    form.widget(preserved_as_paper=checkbox.SingleCheckBoxFieldWidget)
    preserved_as_paper = schema.Bool(
        title=_(u'label_preserved_as_paper', default='Preserved as paper'),
        description=_(u'help_preserved_as_paper', default=''),
        required=False,
        default=True,
        )

    form.omitted('archival_file')
    archival_file = NamedBlobFile(
        title=_(u'label_archival_file', default='Archival File'),
        description=_(u'help_archival_file', default=''),
        required=False,
        )

    form.omitted('thumbnail')
    thumbnail = NamedBlobFile(
        title=_(u'label_thumbnail', default='Thumbnail'),
        description=_(u'help_thumbnail', default=''),
        required=False,
        )

    form.omitted('preview')
    preview = NamedBlobFile(
        title=_(u'label_preview', default='Preview'),
        description=_(u'help_preview', default=''),
        required=False,
        )

    receipt_date = schema.Date(
        title=_(u'label_receipt_date', default='Date of receipt'),
        description=_(u'help_receipt_date', default=''),
        required=False,
        )
    #workaround because ftw.datepicker wasn't working
    form.widget(receipt_date=DatePickerFieldWidget)

    delivery_date = schema.Date(
        title=_(u'label_delivery_date', default='Date of delivery'),
        description=_(u'help_delivery_date', default=''),
        required=False,
        )
    #workaround because ftw.datepicker wasn't working
    form.widget(delivery_date=DatePickerFieldWidget)

    @invariant
    def title_or_file_required(data):
        if not data.title and not data.file:
            raise Invalid(_(u'error_title_or_file_required',
                            default=u'Either the title or the file is '
                            'required.'))

    @invariant
    def file_or_preserved_as_paper(data):
        """ When no digital file exist, the document must be
        preserved in paper.
        """
        if not data.file and not data.preserved_as_paper:
            raise Invalid(
                _(u'error_file_and_preserved_as_paper',
                default=u"You don't select a file and document is also not \
                preserved in paper_form, please correct it."))


# Default values
@form.default_value(field=IDocumentSchema['document_date'])
def default_document_date(data):
    """Set the actual date as default document_date"""
    return date.today()


class Document(Item):

    # disable file preview creation when modifying or creating document
    buildPreview = False

    def Title(self):
        # this is a CMF-style accessor, so should return utf8-encoded
        title = self.title
        if isinstance(title, unicode):
            title = self.title.encode('utf8')
        return self.title or ''

    def surrender(self, relative_to_portal=1):
        return super(Document, self).getIcon(
            relative_to_portal=relative_to_portal)

    def getIcon(self, relative_to_portal=1):
        """Calculate the icon using the mime type of the file
        """
        utool = getToolByName(self, 'portal_url')

        mimetypeitem = self.get_mimetype()
        if not mimetypeitem:
            return self.surrender(relative_to_portal)

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

    def get_mimetype(self):
        """Return the mimetype as object. If there is no matching mimetype,
           it returns False.
        """
        mtr = getToolByName(self, 'mimetypes_registry', None)

        field = self.file
        if not field or not field.getSize():
            # there is no file
            return False

        # get icon by content type
        contenttype = field.contentType
        mimetypeitem = None
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException, msg:
            LOG.error(
                'MimeTypeException for %s. Error is: %s' % (
                    self.absolute_url(), str(msg)))
        if not mimetypeitem:
            # not found
            return False
        return mimetypeitem


@indexer(IDocumentSchema)
def related_items(obj):
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)

    try:
        obj_id = intids.getId(aq_base(obj))
    # In some cases we might not have an intid yet.
    except KeyError:
        return None

    results = []
    relations = catalog.findRelations(
        {'to_id': obj_id, 'from_attribute': 'relatedItems'})
    for rel in relations:
        results.append(rel.from_id)
    return results


grok.global_adapter(related_items, name='related_items')


class SearchableTextExtender(grok.Adapter):
    """Specifix SearchableText Extender for document"""

    grok.context(IDocumentSchema)
    grok.name('IDocumentSchema')
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

        return ' '.join(searchable)


@indexer(IDocumentSchema)
def document_author(obj):
    """document_author indexer"""

    context = aq_inner(obj)
    if not context.document_author:
        return None
    elif isinstance(context.document_author, unicode):
        return context.document_author.encode('utf-8')
    else:
        return context.document_author
grok.global_adapter(document_author, name='document_author')


@indexer(IDocumentSchema)
def document_date(obj):
    """document_date indexer"""

    context = aq_inner(obj)
    if not context.document_date:
        return None
    return context.document_date
grok.global_adapter(document_date, name='document_date')


@indexer(IDocumentSchema)
def receipt_date(obj):
    """receipt_date indexer, can handle None Value"""
    context = aq_inner(obj)
    if not context.receipt_date:
        return None
    return context.receipt_date
grok.global_adapter(receipt_date, name='receipt_date')


@indexer(IDocumentSchema)
def delivery_date(obj):
    """delivery_date indexer"""
    context = aq_inner(obj)
    if not context.delivery_date:
        return None
    return context.delivery_date
grok.global_adapter(delivery_date, name='delivery_date')


@indexer(IDocumentSchema)
def checked_out(obj):
    """checked_out indexer, save the userid of the
    Member who checked the document out"""
    manager = queryMultiAdapter((obj, obj.REQUEST), ICheckinCheckoutManager)
    if not manager:
        return ''

    value = manager.checked_out()
    if value:
        return value

    else:
        return ''
grok.global_adapter(checked_out, name='checked_out')


@indexer(IDocumentSchema)
def sortable_author(obj):
    """Index to allow users to sort on document_author."""
    author = obj.document_author
    if author:
        readable_author = readable_ogds_author(obj, author)
        return readable_author
    return ''
grok.global_adapter(sortable_author, name='sortable_author')


@grok.subscribe(IDocumentSchema, IObjectCreatedEvent)
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def set_digitally_available(doc, event):
    """set the digitally_available field,
    if a file exist the document is digital available"""

    if doc.file:
        doc.digitally_available = True
    else:
        doc.digitally_available = False


@grok.subscribe(IDocumentSchema, IObjectCreatedEvent)
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def sync_title_and_filename_handler(doc, event):
    """Syncs the document and the filename (#586):
    o If there is no title but a file, use the filename (without extension) as
    title.
    o If there is a title and a file, use the normalized title as filename
    """
    normalize_method = getUtility(IIDNormalizer).normalize

    if not doc.title and doc.file:
        # use the filename without extension as title
        filename = doc.file.filename
        doc.title = filename[:filename.rfind('.')]

    elif doc.title and doc.file:
        # use the title as filename
        filename = doc.file.filename
        doc.file.filename = normalize_method(doc.title) + \
            filename[filename.rfind('.'):]


@grok.subscribe(IDocumentSchema, IObjectCopiedEvent)
def set_copyname(doc, event):
    """Documents wich are copied, should be renamed to copy of filename
    """

    key = 'prevent-copyname-on-document-copy'
    request = getRequest()

    if request.get(key, False):
        return
    doc.title = u'%s %s' % (
        translate(_('copy_of', default="copy of"), context=request),
        doc.title)


class View(dexterity.DisplayForm):
    grok.context(IDocumentSchema)
    grok.require("zope2.View")

    def author_link(self):
        info = getUtility(IContactInformation)
        if self.context.document_author:
            return info.render_link(self.context.document_author)
        return None


class ForwardViewlet(grok.Viewlet):
    """Display the message subject
    """
    grok.name('opengever.document.ForwardViewlet')
    grok.context(IDocumentSchema)
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContentTitle)

    def render(self):
        if self.request.get("externaledit", None):
            return '<script language="JavaScript">jq(function(){window.location.href="' + str(
                self.context.absolute_url()) + '/external_edit"})</script>'
        return ''


class Overview(DisplayForm, OpengeverTab):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def get_referenced_documents(self):
        pc = self.context.portal_catalog
        return pc({'portal_type': 'Document', })

    def creator_link(self):
        info = getUtility(IContactInformation)
        return info.render_link(self.context.Creator())


class RelatedTasks(Tasks):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-tasks')

    search_options = {'related_items': related_document}

    def update_config(self):
        Tasks.update_config(self)

        # do not search on this context, search on site
        self.filter_path = None
