from DateTime import DateTime
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.events.events import JournalEntryEvent
from opengever.base.oguid import Oguid
from opengever.journal import _
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from plone.app.textfield import RichText
from plone.restapi.interfaces import IFieldDeserializer
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.globalrequest import getRequest
from zope.schema.interfaces import IVocabularyFactory


MANUAL_JOURNAL_ENTRY = 'manually-journal-entry'

comment_field = RichText(default_mime_type='text/html', output_mime_type='text/x-html-safe')


class AutoEntryManipulationException(Exception):
    """
    """


class JournalManager(object):
    def __init__(self, context):
        self.context = context

    def validate(self, data):
        # validate time:
        value = data.get("time")
        if value and not isinstance(value, DateTime):
            raise ValueError("time should be a zope DateTime not {}".format(type(value)))

    def add_manual_entry(self, category, comment, documents=None, time=None, actor=None):
        if actor is None:
            actor = api.user.get_current().getId()
        entry_obj = {'obj': self.context,
                     'action': PersistentDict({
                         'type': MANUAL_JOURNAL_ENTRY,
                         'category': category,
                         'title': self._get_manual_entry_title(category),
                         'visible': True,
                         'documents': self._serialize_documents(documents)}),
                     'actor': actor,
                     'comment': self._serialize_comment(comment),
                     'time': time}

        self.validate(entry_obj)
        self._notify_journal_event(entry_obj)

    def add_auto_entry(self, action, title, visible=True,
                       comment='', actor=None, documents=None):
        event_obj = {'obj': self.context,
                     'action': PersistentDict({
                         'type': action,
                         'title': title,
                         'visible': visible,
                         'documents': self._serialize_documents(documents),
                     }),
                     'actor': actor,
                     'comment': comment}

        self.validate(event_obj)
        self._notify_journal_event(event_obj)

    def clear(self):
        annotations = IAnnotations(self.context)
        if JOURNAL_ENTRIES_ANNOTATIONS_KEY in annotations:
            del IAnnotations(self.context)[JOURNAL_ENTRIES_ANNOTATIONS_KEY]

    def count(self):
        return len(self.list())

    def list(self):
        return IAnnotations(self.context).get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])

    def lookup(self, entry_id):
        for journal_entry in self.list():
            if journal_entry.get('id') == entry_id:
                return journal_entry

        raise KeyError("Entry '{}' does not exist.".format(entry_id))

    def remove(self, entry_id):
        entry = self.lookup(entry_id)
        if not self._is_manual_entry(entry):
            raise AutoEntryManipulationException()

        self.list().remove(entry)

    def _is_manual_entry(self, entry):
        return entry.get('action', {}).get('type') == MANUAL_JOURNAL_ENTRY

    def update(self, entry_id, **kwargs):
        entry = self.lookup(entry_id)
        entry_action = entry.get('action')
        if not self._is_manual_entry(entry):
            raise AutoEntryManipulationException

        if 'comment' in kwargs:
            entry['comments'] = self._serialize_comment(kwargs.get('comment'))

        if 'documents' in kwargs:
            entry_action['documents'] = self._serialize_documents(kwargs.get('documents'))

        if 'category' in kwargs:
            category = kwargs.get('category')
            entry_action['category'] = category
            entry_action['title'] = self._get_manual_entry_title(category)

        if 'time' in kwargs:
            entry['time'] = kwargs.get('time')

        self.validate(entry)

    def _notify_journal_event(self, event_obj):
        notify(JournalEntryEvent(**event_obj))

    def _serialize_comment(self, comment):
        if not comment:
            return ''

        deserializer = getMultiAdapter(
            (comment_field, self.context, getRequest()), IFieldDeserializer)
        return deserializer(comment).output

    def _serialize_documents(self, documents):
        """Returns a persistent list of dicts with the following data for for
        all documents:

        id: oguid
        title: document title
        """
        value = PersistentList()
        if documents is not None:
            for doc in documents:
                value.append(PersistentDict(
                    {'id': Oguid.for_object(doc).id, 'title': doc.title}))

        return value

    def _get_manual_entry_title(self, category):
        msg = _(u'label_manual_journal_entry',
                default=u'Manual entry: ${category}',
                mapping={'category': self._get_category_title(category)})

        return msg

    def _get_category_title(self, category):
        voca_factory = getUtility(
            IVocabularyFactory,
            name='opengever.journal.manual_entry_categories')

        return voca_factory(self.context).getTerm(category).title
