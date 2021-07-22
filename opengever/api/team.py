from opengever.base.model import create_session
from opengever.ogds.base.browser.team_forms import ITeam
from opengever.ogds.models.team import Team
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxfields import ChoiceFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema import getFields
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ValidationError


class TeamGet(Service):
    """API Endpoint that returns a single team from ogds.

    GET /@teams/team.id HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(TeamGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    def reply(self):
        teamid = self.read_params()
        team = Team.query.get(teamid)
        serializer = queryMultiAdapter((team, self.request), ISerializeToJson)
        return serializer()

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply team ID as URL path parameter.")

        return self.params[0]


class TeamPost(Service):

    schema = ITeam
    model_class = Team

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = self.extract_data()
        team = self.create(data)
        serialized = queryMultiAdapter((team, self.request), ISerializeToJson)()

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", serialized['@id'])

        return serialized

    def extract_data(self, existing_model=None):
        request_data = json_body(self.request)
        data = {}

        errors = []
        # Make sure dxcontent deserializers are used

        for name, field in getFields(self.schema).items():
            value = request_data.get(name)
            if value is None and existing_model:
                value = getattr(existing_model, name)

            if IChoice.providedBy(field):
                # The ChoiceFieldDeserializer is only registered for dx objects
                # but our context is the plone site
                deserializer = ChoiceFieldDeserializer(
                    field, self.context, self.request)
            else:
                deserializer = queryMultiAdapter(
                    (field, self.context, self.request), IFieldDeserializer)

            try:
                data[name] = deserializer(value)
            except ValueError as e:
                errors.append({"message": str(e), "field": name, "error": e})
            except ValidationError as e:
                errors.append({"message": e.doc(), "field": name, "error": e})

        if errors:
            raise BadRequest(errors)

        return data

    def create(self, data):
        obj = self.model_class(**data)
        session = create_session()
        session.add(obj)
        session.flush()
        return obj
