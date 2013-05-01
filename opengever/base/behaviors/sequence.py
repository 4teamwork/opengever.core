from five import grok
from zope.component import getUtility
from plone.indexer import indexer
from plone.directives import form
from opengever.base.interfaces import ISequenceNumber
from zope.lifecycleevent.interfaces import IObjectCopiedEvent


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


@grok.subscribe(ISequenceNumberBehavior, IObjectCopiedEvent)
def new_sequence_number(obj, event):
    """When a object was copied, the sequence number,
    would also be copied. This Event handler fix that problem,
    and generate a new one for the copy."""

    seqNumb = getUtility(ISequenceNumber)
    seqNumb.remove_number(obj)
    seqNumb.get_number(obj)
