from opengever.base.interfaces import ISequenceNumber
from plone.indexer import indexer
from plone.supermodel import model
from zope.component import getUtility


class ISequenceNumberBehavior(model.Schema):
    """the SequenceNumber Behavior is only used
    for the sequence number indexer """
    pass


@indexer(ISequenceNumberBehavior)
def sequence_number(obj):
    """ Indexer for the sequence_number """
    seqNumb = getUtility(ISequenceNumber)
    return seqNumb.get_number(obj)


def new_sequence_number(obj, event):
    """When a object was copied, the sequence number,
    would also be copied. This Event handler fix that problem,
    and generate a new one for the copy."""

    seqNumb = getUtility(ISequenceNumber)
    seqNumb.remove_number(obj)
    seqNumb.get_number(obj)
