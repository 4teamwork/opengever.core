from opengever.ris.proposal import IProposal
from plone.indexer import indexer


@indexer(IProposal)
def committee(obj):
    """String indexer for the SPV committee name"""
    return "riscommittee:{}".format(obj.id)
