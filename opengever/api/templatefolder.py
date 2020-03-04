from opengever.dossier.command import CreateDocumentFromTemplateCommand
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory


class DocumentFromTemplatePost(Service):
    """API Endpoint to create a document in a dossier from a template.
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json_body(self.request)

        token = data.get('template')
        if isinstance(token, dict):
            token = token.get('token')

        if not token:
            raise BadRequest('Missing parameter template')

        vocabulary = getUtility(IVocabularyFactory,
                             name='opengever.dossier.DocumentTemplatesVocabulary')
        term = vocabulary(self.context).getTermByToken(token)
        template = term.value

        title = data.get('title')
        if not title:
            raise BadRequest('Missing parameter title')

        command = CreateDocumentFromTemplateCommand(
            self.context, template, title)
        document = command.execute()

        serializer = queryMultiAdapter((document, self.request), ISerializeToJson)
        return serializer()
