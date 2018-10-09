from opengever.base.behaviors.changed import IChanged
from opengever.base.behaviors.changed import IChangedMarker
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import IReferenceNumber
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from zope.annotation import IAnnotations
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY


@indexer(IDexterityContent)
def referenceIndexer(obj):
    ref_number = IReferenceNumber(obj).get_number()
    return ref_number


@indexer(IDexterityContent)
def title_de_indexer(obj):
    if ITranslatedTitleSupport.providedBy(obj):
        return ITranslatedTitle(obj).title_de
    return None


@indexer(IDexterityContent)
def title_fr_indexer(obj):
    if ITranslatedTitleSupport.providedBy(obj):
        return ITranslatedTitle(obj).title_fr
    return None


@indexer(IDexterityContent)
def bundle_guid_indexer(obj):
    """Indexes the GUID of an item imported from an OGGBundle.

    The corresponding index will only exist temporarily during migrations.
    See openever.bundle.console.add_guid_index()
    """
    return IAnnotations(obj).get(BUNDLE_GUID_KEY)


@indexer(IDexterityContent)
def changed_indexer(obj):
    if IChangedMarker.providedBy(obj):
        # The indexer transforms this to UTC and then represents it as a integer
        return IChanged(obj).changed
    return None
