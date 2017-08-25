from opengever.trash.trash import ITrashed
from plone.indexer import indexer
from zope.interface import Interface


@indexer(Interface)
def trashed_indexer(obj):
    """Indexer for the `trashed` index, this index is used to filter trashed
    documents from catalog search results by default. For that we monkey patch
    the catalog tool's searchResults(), see the patch in opengever.base.monkey.
    """

    return ITrashed.providedBy(obj)
