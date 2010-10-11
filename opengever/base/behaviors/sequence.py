from five import grok
from zope.component import getUtility
from plone.indexer import indexer
from plone.directives import form
from opengever.base.interfaces import ISequenceNumber


class ISequenceNumberBehavior(form.Schema):
    """the SequenceNumber Behavior is only used
    for the sequence number indexer """
    pass

@indexer(ISequenceNumberBehavior)
def sequence_number(obj):
    """ Indexer for the sequence_number """
    seqNumb = getUtility(ISequenceNumber)
    return seqNumb.get_number(obj)
grok.global_adapter(sequence_number, name='sequence_number')
