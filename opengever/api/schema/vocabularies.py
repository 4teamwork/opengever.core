from opengever.base.interfaces import IDuringContentCreation
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.vocabularies.get import VocabulariesGet
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory


class GEVERVocabulariesGet(VocabulariesGet):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        super(GEVERVocabulariesGet, self).__init__(context, request)

    def reply(self):
        if len(self.params) == 0:
            # Listing of existing vocabularies
            return [
                {
                    "@id": "{}/@vocabularies/{}".format(
                        self.context.absolute_url(), vocab[0]
                    ),
                    "title": vocab[0],
                }
                for vocab in getUtilitiesFor(IVocabularyFactory)
            ]

        elif len(self.params) == 1:
            # Edit intent
            # - context is the object to be edited
            self.intent = 'edit'
            vocab_name = self.params[0]
        elif len(self.params) == 2:
            # Add intent
            # - context is the container where the object will be created
            # - first parameter is the portal_type
            #   (which will be ignored by this endpoint, but is accepted
            #   for consistency with @sources and @querysources)
            self.intent = 'add'
            vocab_name = self.params[1]
            alsoProvides(self.request, IDuringContentCreation)
        else:
            return self._error(
                400, "Bad Request",
                "Must supply either zero, one (vocab_name) or "
                "two (portal_type, vocab_name) parameters"
            )

        try:
            factory = getUtility(IVocabularyFactory, name=vocab_name)
        except ComponentLookupError:
            return self._error(
                404, "Not Found", "The vocabulary '{}' does not exist".format(vocab_name)
            )

        vocabulary = factory(self.context)

        serializer = getMultiAdapter(
            (vocabulary, self.request), interface=ISerializeToJson
        )
        return serializer(
            "{}/@vocabularies/{}".format(self.context.absolute_url(), vocab_name)
        )
