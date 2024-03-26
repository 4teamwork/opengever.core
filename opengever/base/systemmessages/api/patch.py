from opengever.api.validation import get_validation_errors
from opengever.api.validation import scrub_json_payload
from opengever.base.model import create_session
from opengever.base.systemmessages.api.base import SystemMessageLocator
from opengever.base.systemmessages.api.schemas import ISystemMessageAPISchema
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


class SystemMessagesPatch(SystemMessageLocator):
    """API endpoint to update an existing system message.

    PATCH /@system-messages/25 HTTP/1.1
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Locate the message to be updated
        sys_msg = self.locate_message()

        # Deserialize JSON payload
        sys_msg_request_data = json_body(self.request)

        # We will serializer the system message instance
        # pop (@id, @type, id, text) from the instance
        # update the instance with the request payload
        # overwrite the serialized instance with the data from request payload
        # send the data to the validation process
        sys_msg_data = getMultiAdapter((sys_msg, self.request), ISerializeToJson)()
        sys_msg_data.pop("@id")
        sys_msg_data.pop("@type")
        sys_msg_data.pop("id")
        sys_msg_data.pop("text")

        for key, value in sys_msg_request_data.items():
            sys_msg_data[key] = value

        scrub_json_payload(sys_msg_data, ISystemMessageAPISchema)
        errors = get_validation_errors(sys_msg_data, ISystemMessageAPISchema, validate_required=False)

        if errors:
            # Structure errors in a way that they can get serialized and
            # translated by the handler in opengever.api.errors
            structured_errors = [{
                'field': field,
                'error': exc.__class__.__name__,
                'message': exc.__class__.__doc__.strip()}
                for field, exc in errors
            ]
            raise BadRequest(structured_errors)

        # Update the system message attributes
        for key, value in sys_msg_data.items():
            setattr(sys_msg, key, value)

        # Commit changes to the database
        session = create_session()
        session.add(sys_msg)
        session.flush()

        # Return the updated system message
        return self.serialize(sys_msg)
