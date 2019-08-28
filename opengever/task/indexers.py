from collective import dexteritytextindexer
from datetime import datetime
from opengever.task.task import ITask
from plone import api
from plone.indexer import indexer
from zope.component import adapter
from zope.interface import implementer


@indexer(ITask)
def date_of_completion(obj):
    # handle 'None' dates. we always need a date for indexing.
    if obj.date_of_completion is None:
        return datetime(1970, 1, 1)
    return obj.date_of_completion


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


@indexer(ITask)
def sequence_number(obj):
    """ Indexer for the sequence_number """
    return obj._sequence_number


@indexer(ITask)
def is_subtask(obj):
    """ is_subtask indexer
    """
    return obj.get_is_subtask()


@implementer(dexteritytextindexer.IDynamicTextIndexExtender)
@adapter(ITask)
class SearchableTextExtender(object):
    """ Task specific SearchableText Extender:
    Adds sequence number and responsible label to the default
    searchabletext."""

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable = []

        lang_tool = api.portal.get_tool('portal_languages')
        for language in lang_tool.getSupportedLanguages():
            if '-' in language:
                language = language.split('-')[0]
            term = self.context.get_task_type_label(language=language)
            if term:
                searchable.append(term.encode('utf-8'))

        searchable.append(str(self.context.get_sequence_number()))
        searchable.append(
            self.context.get_responsible_actor().get_label().encode('utf-8'))

        return ' '.join(searchable)
