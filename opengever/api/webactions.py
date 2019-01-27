from opengever.webactions.exceptions import ActionAlreadyExists
from opengever.webactions.schema import IPersistedWebActionSchema
from opengever.webactions.schema import IWebActionSchema
from opengever.webactions.storage import get_storage
from opengever.webactions.validation import get_validation_errors
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import _no_content_marker
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.component.hooks import getSite
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema import Choice
from zope.schema import List


class WebActionLocator(Service):
    """Locates a webaction by its action_id.

    This is a Service base class for all services that need to look up a
    web action via an /@webactions/{action_id} style URL.

    It handles
    - extraction of the {action_id} path parameter
    - error response for incorrect number of path parameters
    - validation of {action_id} as an integer (and error response)
    - return of a 404 Not Found response if that action doesn't exist
    - retrieval of the respective action

    in a single place so that not every service has to implement this again,
    and we ensure consistent behavior across all services.

    Because the GET service supports both individual retrieval as well as
    listing, this needs to be handled here as well.
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(WebActionLocator, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@webactions as parameters
        self.params.append(name)
        return self

    def _parse_action_id(self):
        action_id_required = getattr(self, 'action_id_required')

        if action_id_required:
            if len(self.params) != 1:
                raise BadRequest(
                    'Must supply exactly one {action_id} path parameter.')
        else:
            # We'll accept zero (listing) or one (get by id) params, but not more
            if len(self.params) > 1:
                raise BadRequest(
                    'Must supply either exactly one {action_id} path parameter '
                    'to fetch a specific webaction, or no parameter for a '
                    'listing of all webactions.')

        # We have a valid number of parameters for the given endpoint
        if len(self.params) == 1:
            try:
                action_id = int(self.params[0])
            except ValueError:
                raise BadRequest('{action_id} path parameter must be an integer')
            return action_id

    def locate_action(self):
        action_id = self._parse_action_id()
        if action_id is not None:
            storage = get_storage()
            try:
                action = storage.get(action_id)
            except KeyError:
                raise NotFound
            return action


class WebActionsPost(Service):
    """API Endpoint to create a new webaction.

    POST /@webactions HTTP/1.1
    """

    def reply(self):
        action_data = json_body(self.request)
        scrub_json_payload(action_data)

        errors = get_validation_errors(action_data, IWebActionSchema)
        if errors:
            raise BadRequest(errors)

        storage = get_storage()
        try:
            action_id = storage.add(action_data)
        except ActionAlreadyExists as exc:
            raise BadRequest([('unique_name', exc)])

        serialized_action = serialize_webaction(storage.get(action_id))

        self.request.response.setStatus(201)
        self.request.response.setHeader('Location', serialized_action['@id'])
        return serialized_action


class WebActionsGet(WebActionLocator):
    """API Endpoint that returns webactions.

    GET /@webactions/42 HTTP/1.1
    GET /@webactions HTTP/1.1
    """

    action_id_required = False

    def reply(self):
        action = self.locate_action()
        if action is not None:
            # Get action by id
            return serialize_webaction(action)
        else:
            # List all actions
            return self.list()

    def list(self):
        site = getSite()
        storage = get_storage()
        actions = storage.list()
        result = {
            '@id': '/'.join((site.absolute_url(), '@webactions')),
            'items': [serialize_webaction(a) for a in actions],
        }
        return result


class WebActionsPatch(WebActionLocator):
    """API Endpoint that updates webactions.

    PATCH /@webactions/42 HTTP/1.1
    """

    action_id_required = True

    def reply(self):
        action = self.locate_action()
        return self.update(action)

    def update(self, action):
        action_delta = json_body(self.request)

        scrub_json_payload(action_delta)

        # Validate on a copy
        action_copy = action.copy()
        action_copy.update(action_delta)
        errors = get_validation_errors(action_copy, IPersistedWebActionSchema)
        if errors:
            raise BadRequest(errors)

        # If validation succeeded, update actual action
        storage = get_storage()

        try:
            storage.update(action['action_id'], action_delta)
        except ActionAlreadyExists as exc:
            raise BadRequest([('unique_name', exc)])

        self.request.response.setStatus(204)
        return _no_content_marker


class WebActionsDelete(WebActionLocator):
    """API Endpoint that deletes a webaction.

    DELETE /@webactions/42 HTTP/1.1
    """

    action_id_required = True

    def reply(self):
        action = self.locate_action()
        return self.delete(action)

    def delete(self, action):
        storage = get_storage()
        # We can't have a KeyError here because action has already been
        # verified as existing by locator
        storage.delete(action['action_id'])

        self.request.response.setStatus(204)
        return _no_content_marker


def serialize_webaction(action):
    """Serialize a webaction.

    `action` can be a PersistentMapping or a dict.
    """
    site = getSite()
    result = dict(action).copy()
    result = json_compatible(result)
    url = '/'.join((site.absolute_url(), '@webactions/%s' % action['action_id']))
    result.update({'@id': url})
    return result


def scrub_json_payload(action_data):
    """Casts some of the unicode strings in JSON payloads to bytestrings.

    Strings in dicts deserialized from JSON are always unicode. But because
    some of the fields as defined in the IWebActionSchema are actually ASCII
    based types (URIs, identifiers that should never contain non-ASCII, etc.)
    we cast them to bytestrings here before even attempting validation.

    In some cases (top-level ASCII fields) validation would fail outright if
    we didn't do this, but in more subtle cases (e.g. Choice fields with
    vocabs that contain ASCII values) this would go unnoticed, and we could
    end up with a mix of bytestrings vs. unicode for the same field in our
    storage, depending on how exactly they were set.
    """
    def safe_utf8(s):
        if isinstance(s, unicode):
            s = s.encode('utf8')
        return s

    for key, value in action_data.items():
        if key in IWebActionSchema:
            field = IWebActionSchema[key]

            # Field itself may be of a bytestring type
            pytype = getattr(field, '_type', None)
            if pytype is str and isinstance(value, unicode):
                action_data[key] = value.encode('utf-8')
                continue

            # Fields vocabulary terms may be of a bytestring type
            if isinstance(field, Choice):
                terms = [t.value for t in field.vocabulary]
                if isinstance(terms[0], str) and isinstance(value, unicode):
                    action_data[key] = value.encode('utf-8')
                    continue

            # Field's value_type may indicate bytestring type
            if isinstance(field, List):
                pytype = getattr(field.value_type, '_type', None)
                if pytype is str and isinstance(value, list):
                    action_data[key] = [safe_utf8(s) for s in value]
                    continue
