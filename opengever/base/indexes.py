from Acquisition import aq_base
from datetime import datetime
from DateTime import DateTime
from five import grok
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import IReferenceNumber
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from zope.component import getMultiAdapter
from zope.interface import Interface


@indexer(IDexterityContent)
def breadcrumb_titlesIndexer(obj):
    breadcrumbs_view = getMultiAdapter((obj, obj.REQUEST),
                                       name='breadcrumbs_view')
    return breadcrumbs_view.breadcrumbs()
grok.global_adapter(breadcrumb_titlesIndexer, name="breadcrumb_titles")


@indexer(IDexterityContent)
def referenceIndexer(obj):
    ref_number = IReferenceNumber(obj).get_number()
    return ref_number
grok.global_adapter(referenceIndexer, name="reference")


@indexer(Interface)
def modified_seconds(obj):
    """The precision of the standard "modified" catalog index is
    minutes. For sensitive features we need a more precise index.
    Running queries against the "modified_seconds" is more
    expensive than running them against the default "modified"
    index - but also more precisie.
    """

    modified = getattr(aq_base(obj), 'modified', None)

    if callable(modified):
        modified = modified()

    if not modified:
        return None

    if isinstance(modified, datetime):
        modified = DateTime(modified)

    return int(modified)  # seconds since the epoch
grok.global_adapter(modified_seconds, name="modified_seconds")


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
