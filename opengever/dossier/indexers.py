from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from five import grok
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.behaviors.filing import IFilingNumberMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossier.utils import get_main_dossier
from opengever.inbox.inbox import IInbox
from opengever.private.dossier import IPrivateDossier
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getAdapter
from zope.component import getUtility


@indexer(IDossierMarker)
def DossierSubjectIndexer(obj):
    aobj = IDossier(obj)
    return aobj.keywords


grok.global_adapter(DossierSubjectIndexer, name="Subject")


@indexer(IDossierTemplateMarker)
def DossierTemplateSubjectIndexer(obj):
    aobj = IDossier(obj)
    return aobj.keywords


grok.global_adapter(DossierTemplateSubjectIndexer, name="Subject")


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
def retention_expiration(obj):
    if IPrivateDossier.providedBy(obj):
        # Private dossiers don't have the Lifecycle behavior, and therefore
        # don't have a retention period, or expiration thereof
        return None
    return obj.get_retention_expiration_date()


grok.global_adapter(retention_expiration, name="retention_expiration")


@indexer(IDossierMarker)
def responsibleIndexer(obj):
    aobj = IDossier(obj)
    if aobj.responsible is None:
        return None
    return aobj.responsible


grok.global_adapter(responsibleIndexer, name="responsible")


@indexer(IDossierMarker)
def isSubdossierIndexer(obj):
    # TODO: should be replaced with the is_subdossier method
    # from og.dossier.base.py
    parent = aq_parent(aq_inner(obj))
    if IDossierMarker.providedBy(parent):
        return True
    return False


grok.global_adapter(isSubdossierIndexer, name="is_subdossier")


@indexer(IDossierTemplateMarker)
def is_subdossier_dossiertemplate(obj):
    return obj.is_subdossier()


grok.global_adapter(is_subdossier_dossiertemplate, name="is_subdossier")


@indexer(IDossierMarker)
def external_reference(obj):
    """Return the external reference of a dossier."""
    context = aq_inner(obj)
    return IDossier(context).external_reference


grok.global_adapter(external_reference, name="external_reference")


@indexer(IDexterityContent)
def main_dossier_title(obj):
    """Return the title of the main dossier."""

    dossier = get_main_dossier(obj)
    if not dossier:
        return None
    try:
        title = dossier.Title()
    except TypeError:
        # XXX: During upgrades, the odd case can happen that a mail inside a
        # forwarding inside the inbox wants to have its containing_dossier
        # reindexed. This can lead to a situation where we attempt to adapt
        # the Inbox to ITranslatedTitle, but it doesn't provide this behavior
        # yet because that behavior is going to be actived in the very same
        # upgrade.
        #
        # Account for this case, and fall back to inbox.title, which
        # will contain the original title (in unicode though).
        if IInbox.providedBy(dossier):
            title = dossier.title.encode('utf-8')
        else:
            raise
    return title


grok.global_adapter(main_dossier_title, name="containing_dossier")


@indexer(IDexterityContent)
def containing_subdossier(obj):
    """Returns the title of the subdossier the object is contained in,
    unless it's contained directly in the root of a dossier, in which
    case an empty string is returned.
    """
    context = aq_inner(obj)
    # Only compute for types that actually can be contained in a dossier
    if context.portal_type not in ['opengever.document.document',
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
        searchable.append(self.context.responsible_label.encode('utf-8'))

        # filing_no
        if IFilingNumberMarker.providedBy(self.context):
            filing_no = getattr(IFilingNumber(self.context), 'filing_no', None)
            if filing_no:
                searchable.append(filing_no.encode('utf-8'))

        # comments
        comments = getattr(IDossier(self.context), 'comments', None)
        if comments:
            searchable.append(comments.encode('utf-8'))

        # keywords
        keywords = IDossier(self.context).keywords
        if keywords:
            searchable.extend(
                keyword.encode('utf-8') if isinstance(keyword, unicode)
                else keyword
                for keyword in keywords)

        external_reference = IDossier(self.context).external_reference
        if external_reference:
            searchable.append(external_reference.encode('utf-8'))

        return ' '.join(searchable)


class DossierTemplateSearchableTextExtender(SearchableTextExtender):
    grok.context(IDossierTemplateMarker)
    grok.name('IDossierTemplate')
    grok.implements(dexteritytextindexer.IDynamicTextIndexExtender)
