from ftw.journal.events.events import JournalEntryEvent
from opengever.base.oguid import Oguid
from opengever.journal import _
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from plone.app.textfield import RichText
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.globalrequest import getRequest
from zope.schema.interfaces import IVocabularyFactory


MANUAL_JOURNAL_ENTRY = 'manually-journal-entry'

comment_field = RichText(default_mime_type='text/html', output_mime_type='text/x-html-safe')


class JournalManager(object):
    def __init__(self, context):
        self.context = context

    def add_manual_entry(self, category, comment, contacts=[], users=[], documents=[]):
        entry_obj = {'obj': self.context,
                     'action': PersistentDict({
                         'type': MANUAL_JOURNAL_ENTRY,
                         'category': category,
                         'title': self._get_manual_entry_title(category),
                         'visible': True,
                         'documents': self._serialize_documents(documents),
                         'contacts': self._serialize_contacts(contacts),
                         'users': self._serialize_users(users)}),
                     'actor': api.user.get_current().getId(),
                     'comment': self._serialize_comment(comment)}

        self._notify_journal_event(entry_obj)

    def add_auto_entry(self, action, title, visible=True,
                       comment='', actor=None, documents=[]):
        event_obj = {'obj': self.context,
                     'action': PersistentDict({
                         'type': action,
                         'title': title,
                         'visible': visible,
                         'documents': self._serialize_documents(documents),
                     }),
                     'actor': actor,
                     'comment': comment}

        self._notify_journal_event(event_obj)

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
        for doc in documents:
            value.append(PersistentDict(
                {'id': Oguid.for_object(doc).id, 'title': doc.title}))

        return value

    def _serialize_contacts(self, contacts):
        """Returns a persistent list of dicts for all contacts.
        """
        value = PersistentList()
        for item in contacts:
            value.append(
                PersistentDict({'id': item.get_contact_id(),
                                'title': item.get_title()}))

        return value

    def _serialize_users(self, users):
        """Returns a persistent list of dicts for all users.
        """
        value = PersistentList()
        for item in users:
            value.append(
                PersistentDict({'id': item.id, 'title': item.get_title()}))

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
