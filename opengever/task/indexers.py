from Acquisition import aq_inner, aq_parent
from collective import dexteritytextindexer
from datetime import datetime
from five import grok
from opengever.base.interfaces import ISequenceNumber
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.task.task import ITask
from plone.indexer import indexer
from zope.component import getUtility


@indexer(ITask)
def date_of_completion(obj):
    # handle 'None' dates. we always need a date for indexing.
    if obj.date_of_completion is None:
        return datetime(1970, 1, 1)
    return obj.date_of_completion
grok.global_adapter(date_of_completion, name='date_of_completion')


@indexer(ITask)
def assigned_client(obj):
    """Indexes the client of the responsible. Since the he may be assigned
    to multiple clients, we need to use the client which was selected in the
    task.
    """

    if not obj.responsible or not obj.responsible_client:
        return ''
    else:
        return obj.responsible_client
grok.global_adapter(assigned_client, name='assigned_client')


@indexer(ITask)
def client_id(obj):
    return get_client_id()
grok.global_adapter(client_id, name='client_id')


@indexer(ITask)
def sequence_number(obj):
    """ Indexer for the sequence_number """
    return obj._sequence_number
grok.global_adapter(sequence_number, name='sequence_number')


@indexer(ITask)
def is_subtask(obj):
    """ is_subtask indexer
    """
    parent = aq_parent(aq_inner(obj))
    return ITask.providedBy(parent)
grok.global_adapter(is_subtask, name='is_subtask')


class SearchableTextExtender(grok.Adapter):
    """ Task specific SearchableText Extender:
    Adds sequence number and responsible label to the default
    searchabletext."""

    grok.context(ITask)
    grok.name('ITask')
    grok.implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable = []


        searchable.append(str(self.context.get_sequence_number()))
        searchable.append(
            self.context.get_responsible_actor().get_label().encode('utf-8'))

        return ' '.join(searchable)
