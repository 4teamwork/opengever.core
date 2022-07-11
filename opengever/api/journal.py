from copy import deepcopy
from opengever.base.helpers import display_name
from opengever.base.oguid import Oguid
from opengever.journal.form import IManualJournalEntry
from opengever.journal.manager import AutoEntryManipulationException
from opengever.journal.manager import JournalManager
from opengever.journal.manager import MANUAL_JOURNAL_ENTRY
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from z3c.form.field import Fields
from zExceptions import BadRequest
from zExceptions import Forbidden
from zExceptions import NotFound
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import ConstraintNotSatisfied


DEFAULT_COMMENT_CATEGORY = 'information'


class JournalService(Service):

    fields = Fields(IManualJournalEntry)

    def __init__(self, context, request):
        super(JournalService, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@journal as parameters
        self.params.append(name)
        return self

    def read_params(self):
        if len(self.params) == 0:
            raise BadRequest("Must supply a journal ID as URL path parameter.")

        if len(self.params) > 1:
            raise BadRequest("Only journal ID is a supported URL path parameter.")

        return self.params[0]

    def _deserialize_data(self, data):
        deserialized_data = {}
        for name, value in data.items():
            field = IManualJournalEntry.get(name)
            if field is None:
                continue

            deserializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldDeserializer)
            deserialized_data[name] = deserializer(value)

        return deserialized_data


class JournalPost(JournalService):
    """Adds a journal-entry"""

    def reply(self):
        data = self._deserialize_data(json_body(self.request))
        comment = data.get('comment')
        category = data.get('category', DEFAULT_COMMENT_CATEGORY)
        documents = data.get('related_documents', [])

        contacts = []
        users = []

        JournalManager(self.context).add_manual_entry(
            category, comment, contacts, users, documents)

        self.request.response.setStatus(204)
        return super(JournalPost, self).reply()


class JournalGet(JournalService):
    """Returns a list of batched journal entries:

    GET /repository/dossier-1/@journal HTTP/1.1
    """
    def reply(self):
        result = {}
        batch = HypermediaBatch(self.request,
                                self._reverse_items(self._filter_items(self._data())))

        result['items'] = self._create_items(batch)
        result['items_total'] = batch.items_total
        if batch.links:
            result['batching'] = batch.links

        return result

    def get_related_documents(self, documents):
        related_documents = []
        for document in documents:
            obj = Oguid.parse(document['id']).resolve_object()
            serialized_document = queryMultiAdapter((obj, self.request), ISerializeToJsonSummary)()
            related_documents.append(serialized_document)
        return related_documents

    def _create_items(self, batch):
        items = []
        for entry in batch:
            action = entry.get('action')
            item = {}
            item['@id'] = '{}/@journal/{}'.format(
                self.context.absolute_url(), entry.get('id'))
            item['id'] = entry.get('id')
            item['is_editable'] = bool(action.get('type') == MANUAL_JOURNAL_ENTRY and entry.get('id'))
            item['title'] = self._item_title(entry)
            item['time'] = json_compatible(entry.get('time'))
            item['actor_id'] = entry.get('actor')
            item['actor_fullname'] = display_name(entry.get('actor'))
            item['comment'] = entry.get('comments')
            item['related_documents'] = self.get_related_documents(action.get('documents', []))
            items.append(item)

        return items

    def _item_title(self, item):
        return translate(item.get('action').get('title'), context=self.request)

    def _data(self):
        return deepcopy(JournalManager(self.context).list())

    def _filter_items(self, items):
        filters = self.request.get('filters', {})
        search = safe_unicode(self.request.get('search', '').lower())

        manual_entries_only = filters.get('manual_entries_only', False)
        categories = filters.get('categories', [])

        filtered_items = []
        for item in items:
            action = item.get('action', {})
            if manual_entries_only:
                if not action.get('type') == MANUAL_JOURNAL_ENTRY:
                    continue

            if categories:
                if action.get('category') not in categories:
                    continue

            if search:
                title = safe_unicode(self._item_title(item).lower())
                comments = safe_unicode(item['comments'].lower())
                if search not in title and search not in comments:
                    continue

            filtered_items.append(item)
        return filtered_items

    def _reverse_items(self, items):
        items.reverse()
        return items


class JournalDelete(JournalService):
    """API Endpoint to delete an existing manual journal entry.

    DELETE /dossier-1/@journal/123 HTTP/1.1
    """

    implements(IPublishTraverse)

    def reply(self):
        entry_id = self.read_params()
        try:
            JournalManager(self.context).remove(entry_id)
        except KeyError:
            raise NotFound()
        except AutoEntryManipulationException:
            raise Forbidden("Only manual journal entries can be removed")

        self.request.response.setStatus(204)
        return None


class JournalPatch(JournalService):
    """API Endpoint to update an existing journal entry.

    PATCH /@journal/123 HTTP/1.1
    {
        "comment": "My new comment",
        "category": "information",
        "related_documents": []
    }
    """
    implements(IPublishTraverse)

    def reply(self):
        entry_id = self.read_params()

        try:
            data = self._deserialize_data(json_body(self.request))
        except (ValueError, ConstraintNotSatisfied) as exc:
            raise BadRequest('%s: %s' % (exc.__class__.__name__, str(exc)))

        if 'related_documents' in data:
            data['documents'] = data.pop('related_documents')

        try:
            JournalManager(self.context).update(entry_id, **data)
        except KeyError:
            raise NotFound()
        except AutoEntryManipulationException:
            raise Forbidden("Only manual journal entries can be updated")

        self.request.response.setStatus(204)
        return None
