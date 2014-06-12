from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from five import grok
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ogds.base.actor import Actor
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getAdapter
from zope.component import getUtility


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
    # TODO: should be replaced with the is_subdossier method
    # from og.dossier.base.py
    parent = aq_parent(aq_inner(obj))
    if IDossierMarker.providedBy(parent):
        return True
    return False
grok.global_adapter(isSubdossierIndexer, name="is_subdossier")


@indexer(IDexterityContent)
def top_dossier_title(obj):
    """return the tilte of the top containing dossier."""
    dossier_title = ''
    while not IPloneSiteRoot.providedBy(obj):
        if IDossierMarker.providedBy(
            obj) or obj.portal_type == 'opengever.inbox.inbox':
            dossier_title = obj.Title()
        obj = aq_parent(aq_inner(obj))
    return dossier_title
grok.global_adapter(top_dossier_title, name="containing_dossier")


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
        searchable.append(
            self.context.get_responsible_actor().get_label().encode('utf-8'))

        dossier = IDossier(self.context)
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
