from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
import json


class RemoteTaskBaseService(Service):
    """Base class for REST API endpoints invoking remote task operations.
    """

    required_params = ()
    optional_params = ()

    required_params = ('transition', )
    optional_params = ('documents', 'text')

    def is_remote(self, oguid):
        return not oguid.is_on_current_admin_unit

    def extract_params(self):
        """Extract and validate required and optional parameters.

        Reject any unknown parameters.
        """
        json_data = json_body(self.request)
        params = {}

        # Required
        for req_name in self.required_params:
            if req_name not in json_data:
                raise BadRequest(
                    'Required parameter "%s" is missing in body' % req_name)

            value = json_data.pop(req_name)
            params[req_name] = value

        # Optional
        for opt_name in self.optional_params:
            if opt_name in json_data:
                params[opt_name] = json_data.pop(opt_name)

        # Reject any left over unexpected parameters
        unexpected_params = json_data.keys()
        if unexpected_params:
            supported_params = self.required_params + self.optional_params
            raise BadRequest(
                'Unexpected parameter(s) in JSON body: %s. '
                'Supported parameters are: %s' % (
                    json.dumps(unexpected_params),
                    json.dumps(supported_params)))

        return params

    def format_exception(self, exc):
        return '%s: %s' % (exc.__class__.__name__, str(exc))

    def serialize(self, obj):
        serializer = queryMultiAdapter(
            (obj, self.request), ISerializeToJson)
        serialized_obj = serializer()
        serialized_obj["@id"] = obj.absolute_url()
        return serialized_obj
