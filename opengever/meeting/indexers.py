from opengever.meeting.proposal import IBaseProposal
from plone.indexer import indexer


@indexer(IBaseProposal)
def committeeIndexer(obj):
    return "committee:{}".format(obj.get_committee().load_model().committee_id)
