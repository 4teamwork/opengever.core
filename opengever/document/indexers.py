from Acquisition import aq_inner
from collective import dexteritytextindexer
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.classification import IClassificationMarker
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IDocumentIndexer
from opengever.ogds.base.actor import Actor
from plone import api
from plone.indexer import indexer
from Products.CMFDiffTool.utils import safe_utf8
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
import logging


logger = logging.getLogger('opengever.document')


@implementer(IDocumentIndexer)
@adapter(Interface)
class DefaultDocumentIndexer(object):
    """Extracts plain text directly from files contained in
    opengever.document.document objects using portal transforms.
    """

    def __init__(self, context):
        self.context = context

    def extract_text(self):
        file_ = self.context.get_file()
        if file_:
            filename = file_.filename
            transform_tool = api.portal.get_tool('portal_transforms')
            try:
                plain_text = transform_tool.convertTo(
                    'text/plain',
                    file_.data,
                    mimetype=file_.contentType,
                    filename=filename,
                    object=file_._blob)
            except ConflictError:
                raise
            except Exception, e:
                logger.warn("Transforming document '%s' to 'text/plain'"
                            "failed with '%s'" % (filename, e))
                return ''

            if plain_text:
                return plain_text.getData()
        return ''


@implementer(dexteritytextindexer.IDynamicTextIndexExtender)
@adapter(IBaseDocument)
class SearchableTextExtender(object):
    """Specifix SearchableText Extender for document"""

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
        if fulltext:
            searchable.append(fulltext)

        # keywords
        keywords = IDocumentMetadata(self.context).keywords
        if keywords:
            searchable.extend(safe_utf8(keyword) for keyword in keywords)

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


@indexer(IDocumentSchema)
def document_date(obj):
    """document_date indexer"""

    context = aq_inner(obj)
    if not context.document_date:
        return None
    return context.document_date


@indexer(IDocumentSchema)
def external_reference(obj):
    """Return the foreign reference of a document."""
    context = aq_inner(obj)
    return IDocumentMetadata(context).foreign_reference


@indexer(IDocumentSchema)
def receipt_date(obj):
    """receipt_date indexer, can handle None Value"""
    context = aq_inner(obj)
    if not context.receipt_date:
        return None
    return context.receipt_date


@indexer(IDocumentSchema)
def delivery_date(obj):
    """delivery_date indexer"""
    context = aq_inner(obj)
    if not context.delivery_date:
        return None
    return context.delivery_date


@indexer(IDocumentSchema)
def checked_out(obj):
    """checked_out indexer, save the userid of the
    Member who checked the document out"""
    manager = queryMultiAdapter((obj, obj.REQUEST), ICheckinCheckoutManager)
    if not manager:
        return ''

    value = manager.get_checked_out_by()
    if value:
        return value

    else:
        return ''


@indexer(IDocumentMetadata)
def sortable_author(obj):
    """Index to allow users to sort on document_author."""
    author = obj.document_author
    if author:
        return Actor.user(author).get_label()
    return ''


@indexer(IDocumentMetadata)
def DocumentSubjectIndexer(obj):
    return IDocumentMetadata(obj).keywords


@indexer(IClassificationMarker)
def public_trial(obj):
    public_trial = IClassification(obj).public_trial
    if public_trial:
        return public_trial

    return ''


@indexer(IBaseDocument)
def metadata(obj):
    metadata = []

    reference_number = IReferenceNumber(obj)
    metadata.append(reference_number.get_number())

    doc_metadata = IDocumentMetadata(obj)
    if doc_metadata.description:
        metadata.append(doc_metadata.description.encode('utf8'))
    if doc_metadata.keywords:
        metadata.extend([k.encode('utf8') for k in doc_metadata.keywords])
    if doc_metadata.foreign_reference:
        metadata.append(doc_metadata.foreign_reference.encode('utf8'))

    return ' '.join(metadata)


@indexer(IBaseDocument)
def filesize(obj):
    file_ = obj.get_file()
    if file_:
        return file_.getSize()
    return 0
