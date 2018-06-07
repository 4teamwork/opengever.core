from Acquisition import aq_inner
from opengever.repository.repositoryfolder import IRepositoryFolder
from plone.i18n.normalizer.base import mapUnicode
from plone.indexer import indexer
from Products.CMFPlone.CatalogTool import MAX_SORTABLE_TITLE
from Products.CMFPlone.CatalogTool import num_sort_regex
from Products.CMFPlone.CatalogTool import zero_fill
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import safe_unicode
import re


@indexer(IRepositoryFolder)
def title_de_indexer(obj):
    return obj.get_prefixed_title_de()


@indexer(IRepositoryFolder)
def title_fr_indexer(obj):
    return obj.get_prefixed_title_fr()


@indexer(IRepositoryFolder)
def blocked_local_roles(obj):
    """Return whether acquisition is blocked or not."""
    return bool(getattr(aq_inner(obj), '__ac_local_roles_block__', False))


@indexer(IRepositoryFolder)
def sortable_title(obj):
    """Custom sortable_title indexer for RepositoryFolders.

    This implementation doesn't count space needed for zero padded numbers
    towards the maximum length. We need this for repofolders because otherwise
    for deeply nested folders the reference numbers alone eat up all
    the available space (40 characters).
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

            # Determine the length of the sortable title
            padded_numbers = re.findall(num_sort_regex, sortabletitle)
            max_length = MAX_SORTABLE_TITLE + sum([
                len(match) - len(match.lstrip('0'))
                for match in padded_numbers
            ])

            # Truncate to prevent bloat, take bits from start and end
            if len(sortabletitle) > max_length:
                start = sortabletitle[:(max_length - 13)]
                end = sortabletitle[-10:]
                sortabletitle = start + '...' + end
            return sortabletitle.encode('utf-8')
    return ''
