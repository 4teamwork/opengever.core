from collective import dexteritytextindexer
from opengever.activity import notification_center
from opengever.activity.roles import WATCHER_ROLE
from opengever.base.utils import unrestrictedPathToCatalogBrain
from opengever.task.task import ITask
from plone import api
from plone.indexer import indexer
from zope.component import adapter
from zope.interface import implementer


@indexer(ITask)
def is_completed(obj):
    """Boolean indexer if the task is completed"""
    return obj.is_in_final_state


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


@indexer(ITask)
def watchers(obj):
    """Index all userids that watch this task in the default watcher role."""

    center = notification_center()
    watchers = center.get_watchers(obj, role=WATCHER_ROLE)
    return [watcher.actorid for watcher in watchers]


@indexer(ITask)
def related_items(obj):
    brains = [unrestrictedPathToCatalogBrain(rel.to_path)
              for rel in ITask(obj).relatedItems if not rel.isBroken()]
    return [brain.UID for brain in brains if brain]
