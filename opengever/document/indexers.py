from Acquisition import aq_inner
from collective import dexteritytextindexer
from opengever.activity import notification_center
from opengever.activity.roles import WATCHER_ROLE
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.classification import IClassificationMarker
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.utils import ensure_str
from opengever.base.utils import unrestrictedPathToCatalogBrain
from opengever.document.approvals import IApprovalList
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IDocumentIndexer
from opengever.document.interfaces import ITemplateDocumentMarker
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
from zope.schema import getFields
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
def document_type(obj):
    return IDocumentMetadata(obj).document_type


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

    custom_properties = IDocumentCustomProperties(obj).custom_properties
    if custom_properties:
        field = getFields(IDocumentCustomProperties).get('custom_properties')
        active_slot = field.get_active_assignment_slot(obj)
        for slot in [active_slot, field.default_slot]:
            for value in custom_properties.get(slot, {}).values():
                if isinstance(value, bool):
                    continue
                elif isinstance(value, list):
                    metadata.extend([ensure_str(item) for item in value])
                else:
                    metadata.append(ensure_str(value))

    return ' '.join(metadata)


@indexer(IBaseDocument)
def filesize(obj):
    file_ = obj.get_file()
    if file_:
        return file_.getSize()
    return 0


@indexer(IBaseDocument)
def filename(obj):
    filename = obj.get_filename()
    if filename:
        return filename
    return u''


@indexer(IBaseDocument)
def file_extension(obj):
    """file_extension indexer for documents and mails.
    For document it returns the extension of the file for mails it returns the
    extension of the original_message file if exists.
    """
    return obj.get_file_extension()


@indexer(IBaseDocument)
def watchers(obj):
    """Index all userids that watch this document in the default watcher role."""
    center = notification_center()
    watchers = center.get_watchers(obj, role=WATCHER_ROLE)
    return [watcher.actorid for watcher in watchers]


@indexer(IBaseDocument)
def approval_state(obj):
    """Indexer for approval_state Solr index.
    """
    approvals = IApprovalList(obj)
    approval_state = approvals.get_approval_state()
    return approval_state


@indexer(ITemplateDocumentMarker)
def containing_dossier_title(obj):
    templatefolder = obj.get_parent_dossier()
    if not templatefolder:
        return None
    languages = api.portal.get_tool('portal_languages').getSupportedLanguages()
    titles = [templatefolder.Title(language.split('-')[0]) for language in languages]
    return ' / '.join(titles)


@indexer(IDocumentSchema)
def related_items(obj):
    brains = [unrestrictedPathToCatalogBrain(rel.to_path)
              for rel in IRelatedDocuments(obj).relatedItems if not rel.isBroken()]
    return [brain.UID for brain in brains if brain]
