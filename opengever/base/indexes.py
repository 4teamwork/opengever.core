from five import grok
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import IReferenceNumber
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer


@indexer(IDexterityContent)
def referenceIndexer(obj):
    ref_number = IReferenceNumber(obj).get_number()
    return ref_number
grok.global_adapter(referenceIndexer, name="reference")


@indexer(IDexterityContent)
def title_de_indexer(obj):
    if ITranslatedTitleSupport.providedBy(obj):
        return ITranslatedTitle(obj).title_de
    return None

grok.global_adapter(title_de_indexer, name="title_de")


@indexer(IDexterityContent)
def title_fr_indexer(obj):
    if ITranslatedTitleSupport.providedBy(obj):
        return ITranslatedTitle(obj).title_fr
    return None

grok.global_adapter(title_fr_indexer, name="title_fr")
