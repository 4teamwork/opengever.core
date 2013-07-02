from Acquisition import aq_inner
from collective import dexteritytextindexer
from datetime import datetime
from five import grok
from opengever.base.interfaces import ISequenceNumber
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.task.task import ITask
from plone.indexer import indexer
from zc.relation.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


@indexer(ITask)
def related_items(obj):
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)

    # object might not have an intid yet
    try:
        obj_intid = intids.getId(aq_inner(obj))
    except KeyError:
        return []

    results = []
    relations = catalog.findRelations({'from_id': obj_intid,
                                       'from_attribute': 'relatedItems'})
    for rel in relations:
        results.append(rel.to_id)
    return results
grok.global_adapter(related_items, name='related_items')


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
    return obj.is_subtask()
grok.global_adapter(is_subtask, name='is_subtask')


class SearchableTextExtender(grok.Adapter):
    """ Task specific SearchableText Extender"""

    grok.context(ITask)
    grok.name('ITask')
    grok.implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable = []
        # append some other attributes to the searchableText index

        # sequence_number
        seqNumb = getUtility(ISequenceNumber)
        searchable.append(str(seqNumb.get_number(self.context)))

        #responsible
        info = getUtility(IContactInformation)
        dossier = ITask(self.context)
        searchable.append(info.describe(dossier.responsible).encode(
                'utf-8'))

        return ' '.join(searchable)
