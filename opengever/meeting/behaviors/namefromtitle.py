from opengever.base.interfaces import ISequenceNumber
from plone.app.content.interfaces import INameFromTitle
from zope.component import getUtility
from zope.interface import implements


class ICommitteeNameFromTitle(INameFromTitle):
    """Special name from title behavior for letting the normalizing name
    chooser choose the ID.
    The id of a committee should be in the format:
    "committee-{sequence number}"
    """


class CommitteeNameFromTitle(object):
    implements(ICommitteeNameFromTitle)

    format = u'committee-{}'

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format.format(seq_number)


class IProposalNameFromTitle(INameFromTitle):
    """Special name from title behavior for letting the normalizing name
    chooser choose the ID.
    The id of a proposal should be in the format: "proposal-{sequence number}"
    """


class ProposalNameFromTitle(object):
    implements(IProposalNameFromTitle)

    format = u'proposal-{}'

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format.format(seq_number)
