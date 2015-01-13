from collective import dexteritytextindexer
from five import grok
from opengever.meeting.proposal import IProposal


class ProposalSearchableTextExtender(grok.Adapter):
    """Add proposal fields to searchable text."""

    grok.context(IProposal)
    grok.name('IProposal')
    grok.implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return self.context.get_searchable_text()
