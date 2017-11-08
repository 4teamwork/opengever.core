from Acquisition import aq_inner
from opengever.repository.repositoryfolder import IRepositoryFolder
from plone.indexer import indexer


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
