from opengever.api.validation import get_validation_errors
from opengever.api.validation import scrub_json_payload
from opengever.base.model import create_session
from opengever.base.systemmessages.api.base import SystemMessagesBase
from opengever.base.systemmessages.api.schemas import ISystemMessageAPISchema
from opengever.base.systemmessages.models import SystemMessage
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from zExceptions import BadRequest
from zope.interface import alsoProvides


class SystemMessagesPost(SystemMessagesBase):
    """API endpoint to create a new system message.

    POST /@system-messages HTTP/1.1
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        sys_msg_data = json_body(self.request)
        scrub_json_payload(sys_msg_data, ISystemMessageAPISchema)
        errors = get_validation_errors(sys_msg_data, ISystemMessageAPISchema)

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

        sys_msg = SystemMessage(
            admin_unit_id=sys_msg_data.get("admin_unit", None),
            text_en=sys_msg_data.get("text_en", None),
            text_de=sys_msg_data.get("text_de", None),
            text_fr=sys_msg_data.get("text_fr", None),
            start_ts=sys_msg_data.get("start_ts"),
            end_ts=sys_msg_data.get("end_ts"),
            type=sys_msg_data.get("type")
        )

        session = create_session()
        session.add(sys_msg)
        session.flush()

        serialized_sys_msg = self.serialize(sys_msg)

        self.request.response.setStatus(201)
        self.request.response.setHeader('Location', serialized_sys_msg['@id'])
        return serialized_sys_msg
