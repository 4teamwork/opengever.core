from Acquisition import aq_base
from opengever.base.behaviors.changed import IChanged
from opengever.base.behaviors.changed import IChangedMarker
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.interfaces import IReferenceNumber
from opengever.base.model import SORTABLE_TITLE_LENGTH
from opengever.bundle.sections.constructor import BUNDLE_GUID_KEY
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from plone.i18n.normalizer.base import mapUnicode
from plone.indexer import indexer
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.CatalogTool import num_sort_regex
from Products.CMFPlone.CatalogTool import zero_fill
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import safe_unicode
from zope.annotation import IAnnotations


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


@indexer(IDexterityContent)
def sortable_title(obj):
    """Custom sortable_title indexer for all content types.

    This is a copy from Products.CMFPlone.CatalogTool.sortable_title
    except that we overwrite MAX_SORTABLE_TITLE with SORTABLE_TITLE_LENGTH.
    We set set it to a high enough value to basically avoid ever cropping
    the title, even with number padding. This is to avoid sorting issues
    in content listings.
    """
    title = getattr(obj, 'Title', None)
    if title is not None:
        if safe_callable(title):
            title = title()

        if isinstance(title, basestring):
            # Ignore case, normalize accents, strip spaces
            sortabletitle = mapUnicode(safe_unicode(title)).lower().strip()
            # Replace numbers with zero filled numbers
            sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
            # Truncate to prevent bloat, take bits from start and end
            if len(sortabletitle) > SORTABLE_TITLE_LENGTH:
                start = sortabletitle[:(SORTABLE_TITLE_LENGTH - 13)]
                end = sortabletitle[-10:]
                sortabletitle = start + u'...' + end
            return sortabletitle.encode('utf-8')
    return ''


@indexer(IFolderish)
def has_sametype_children(obj):
    # child objects are acquisition wrapped, so any child.portal_type would
    # return the obj.portal_type if the child object does not have a
    # portal_type attribute.
    return any(obj.portal_type == getattr(aq_base(child), "portal_type", None)
               for child in obj.objectValues())


@indexer(IDexterityContent)
def is_subdossier(obj):
    return None
