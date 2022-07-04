from copy import deepcopy
from opengever.base.helpers import display_name
from opengever.base.oguid import Oguid
from opengever.base.vocabulary import voc_term_title
from opengever.journal.form import IManualJournalEntry
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
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import RequiredMissing


DEFAULT_COMMENT_CATEGORY = 'information'


class JournalService(Service):

    fields = Fields(IManualJournalEntry)

    def _validate_category(self, category):
        """Validates if the given category exists in the journal category
        vocabulary.

        :param category: string of category-term

        :return true if valid, false if invalid
        """
        try:
            voc_term_title(self.fields['category'].field, category)
            return True
        except LookupError:
            raise BadRequest("The provided 'category' does not exists.")

    def _lookup_documents(self, related_documents):
        """Lookups documents based on the url.

        :param related_documents: list of urls to related documents

        :return list of document-objects, list of invalid-urls
        """
        deserializer = queryMultiAdapter(
            (self.fields['related_documents'].field, self.context, self.request),
            IFieldDeserializer)

        documents = []
        invalid_urls = []

        for document_url in related_documents:
            try:
                documents.append(deserializer(document_url)[0])
            except (RequiredMissing, ConstraintNotSatisfied):
                invalid_urls.append(document_url)

        if invalid_urls:
            raise BadRequest(
                "Could not lookup the following documents: {}".format(
                    ', '.join(invalid_urls)))

        return documents


class JournalPost(JournalService):
    """Adds a journal-entry"""

    def reply(self):
        data = json_body(self.request)
        category = data.get('category', DEFAULT_COMMENT_CATEGORY)
        comment = data.get('comment')

        if not comment:
            raise BadRequest("The request body requires the 'comment' attribute")

        self._validate_category(category)

        documents = self._lookup_documents(
            data.get('related_documents', []))

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
            item['title'] = self._item_title(entry)
            item['time'] = json_compatible(entry.get('time'))
            item['actor_id'] = entry.get('actor')
            item['actor_fullname'] = display_name(entry.get('actor'))
            item['comments'] = entry.get('comments')
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
