from copy import deepcopy
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from opengever.base.helpers import display_name
from opengever.base.vocabulary import voc_term_title
from opengever.journal.entry import ManualJournalEntry
from opengever.journal.form import IManualJournalEntry
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from z3c.form.field import Fields
from zExceptions import BadRequest
from zope.annotation.interfaces import IAnnotations
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import RequiredMissing


DEFAULT_COMMENT_CATEGORY = 'information'


class JournalPost(Service):
    """Adds a journal-entry"""

    fields = Fields(IManualJournalEntry)

    def reply(self):
        data = json_body(self.request)
        category = data.get('category', DEFAULT_COMMENT_CATEGORY)
        comment = data.get('comment')

        if not comment:
            raise BadRequest("The request body requires the 'comment' attribute")

        if not self._validate_category(category):
            raise BadRequest("The provided 'category' does not exists.")

        documents, invalid_urls = self._lookup_documents(
            data.get('related_documents', []))

        if invalid_urls:
            raise BadRequest(
                "Could not lookup the following documents: {}".format(
                    ', '.join(invalid_urls)))

        contacts = []
        users = []

        entry = ManualJournalEntry(self.context,
                                   category,
                                   comment,
                                   contacts,
                                   users,
                                   documents)
        entry.save()

        self.request.response.setStatus(204)
        return super(JournalPost, self).reply()

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

        return documents, invalid_urls

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
            return False


class JournalGet(Service):
    """Returns a list of batched journal entries:

    GET /repository/dossier-1/@journal HTTP/1.1
    """
    def reply(self):
        result = {}
        batch = HypermediaBatch(self.request, self._data())

        result['items'] = self._create_items(batch)
        result['items_total'] = batch.items_total
        if batch.links:
            result['batching'] = batch.links

        return result

    def _create_items(self, batch):
        items = []
        for entry in batch:
            action = entry.get('action')
            item = {}
            item['title'] = translate(action.get('title'), context=self.request)
            item['time'] = json_compatible(entry.get('time'))
            item['actor_id'] = entry.get('actor')
            item['actor_fullname'] = display_name(entry.get('actor'))
            item['comments'] = entry.get('comments')
            items.append(item)

        return items

    def _data(self):
        annotations = IAnnotations(self.context)
        items = deepcopy(annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, []))
        items.reverse()
        return items
