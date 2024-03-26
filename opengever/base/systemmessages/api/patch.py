from opengever.api.validation import get_validation_errors
from opengever.api.validation import scrub_json_payload
from opengever.base.model import create_session
from opengever.base.systemmessages.api.base import SystemMessageLocator
from opengever.base.systemmessages.api.schemas import ISystemMessageAPISchema
from opengever.ogds.models.service import ogds_service
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from zExceptions import BadRequest
from zope.interface import alsoProvides


class SystemMessagesPatch(SystemMessageLocator):
    """API endpoint to update an existing system message.

    PATCH /@system-messages/25 HTTP/1.1
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        patch_data = json_body(self.request)

        existing_msg = self.locate_message()
        scrub_json_payload(patch_data, ISystemMessageAPISchema)

        # We will serializer the system message instance `existing_msg`
        # pop (@id, @type, id, text, active) from the existing_msg_serialized
        # overwrite existing_msg values with the request data `sys_msg_request_data`
        # overwrite the serialized instance with the data from request payload
        # send the data to the validation process

        existing_msg_serialized = self.serialize(existing_msg)
        existing_msg_serialized.pop("@id")
        existing_msg_serialized.pop("@type")
        existing_msg_serialized.pop("id")
        existing_msg_serialized.pop("text")
        existing_msg_serialized.pop("active")

        existing_msg_serialized.update(patch_data)

        scrub_json_payload(existing_msg_serialized, ISystemMessageAPISchema)
        errors = get_validation_errors(existing_msg_serialized, ISystemMessageAPISchema)
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

        for key, value in patch_data.items():
            if key == "admin_unit" and value:
                admin = ogds_service().fetch_admin_unit(value)
                setattr(existing_msg, key, admin)
            else:
                setattr(existing_msg, key, value)

        session = create_session()
        session.add(existing_msg)
        session.flush()
        serialized_sys_msg = self.serialize(existing_msg)
        self.request.response.setStatus(200)
        self.request.response.setHeader('Location', serialized_sys_msg['@id'])
        return serialized_sys_msg
