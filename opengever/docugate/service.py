from opengever.officeconnector.service import OfficeConnectorPayload
from plone import api
from zExceptions import Forbidden
import json


class OfficeConnectorDocugatePayload(OfficeConnectorPayload):
    """Issue JSON instruction payloads for OfficeConnector.

    Contains the instruction set to generate a document from a docugate
    template (Docugate-XML), then checkout the corresponding document (checkout-url)
    to open the created document in an editor. From there the normal checkout,
    checkin cycle can begin.
    """

    @staticmethod
    def document_is_valid(document):
        return document and document.is_shadow_document()

    def render(self):
        payloads = self.get_base_payloads()

        for payload in payloads:
            # A permission check to verify the user is also able to upload
            authorized = api.user.has_permission(
                'Modify portal content',
                obj=payload['document'],
            )

            if authorized:
                del payload['document']
                payload['docugate-xml'] = '@@docugate-xml'

            else:
                # Fail per default
                raise Forbidden

        self.request.response.setHeader('Content-type', 'application/json')

        return json.dumps(payloads)
