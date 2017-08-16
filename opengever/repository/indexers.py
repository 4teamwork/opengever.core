from opengever.repository.repositoryfolder import IRepositoryFolder
from plone.indexer import indexer


@indexer(IRepositoryFolder)
def title_de_indexer(obj):
    return obj.get_prefixed_title_de()


@indexer(IRepositoryFolder)
def title_fr_indexer(obj):
    return obj.get_prefixed_title_fr()
