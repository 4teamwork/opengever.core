from Acquisition import aq_inner, aq_base
from collective import dexteritytextindexer
from five import grok
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IDocumentIndexer
from opengever.tabbedview.helper import readable_ogds_author
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName
from zc.relation.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, queryMultiAdapter, getAdapter
from zope.interface import Interface


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


class DefaultDocumentIndexer(grok.Adapter):
    """Extracts plain text directly from files contained in
    opengever.document.document objects using portal transforms.
    """

    grok.context(Interface)
    grok.implements(IDocumentIndexer)

    def __init__(self, context):
        self.context = context

    def extract_text(self):
        if self.context.file:
            transform_tool = getToolByName(self.context, 'portal_transforms')
            plain_text = transform_tool.convertTo(
                'text/plain',
                self.context.file.data,
                mimetype=self.context.file.contentType,
                filename=self.context.file.filename,
                object=self.context.file)

            if plain_text:
                return plain_text.getData()
        return ''


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

        fulltext_indexer = getAdapter(self.context, IDocumentIndexer)
        fulltext = fulltext_indexer.extract_text()
        searchable.append(fulltext)

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
