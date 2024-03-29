from ftw.mail.mail import IMail
from opengever.api.deserializer import GeverDeserializeFromJson
from opengever.api.document import SerializeDocumentToJson
from opengever.api.not_reported_exceptions import Forbidden as NotReportedForbidden
from opengever.base.transforms.msg2mime import Msg2MimeTransform
from opengever.mail import _ as mail_mf
from opengever.mail.exceptions import AlreadyExtractedError
from opengever.mail.exceptions import InvalidAttachmentPosition
from opengever.mail.mail import initialize_metadata
from opengever.mail.mail import initialize_title
from plone.app.uuid.utils import uuidToURL
from plone.namedfile.file import NamedBlobFile
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface


# Convert .msg files to .eml and store the .msg in the 'original_message'
# field.
@implementer(IDeserializeFromJson)
@adapter(IMail, Interface)
class DeserializeMailFromJson(GeverDeserializeFromJson):

    def __call__(self, validate_all=False, data=None, create=False):
        if data is None:
            data = json_body(self.request)

        context = super(DeserializeMailFromJson, self).__call__(
            validate_all=validate_all, data=data, create=create)

        if context.message and context.message.filename.lower().endswith('.msg'):
            self.context.original_message = context.message
            transform = Msg2MimeTransform()
            eml = transform.transform(context.message.data)
            file_ = NamedBlobFile(
                data=eml,
                filename=context.message.filename[:-3] + 'eml',
                contentType='message/rfc822')
            context.message = file_

        if create and 'message' in data:
            if not data.get('title'):
                context._update_title_from_message_subject()
                initialize_title(context, None)

            initialize_metadata(context, None)

        return context


@implementer(ISerializeToJson)
@adapter(IMail, Interface)
class SerializeMailToJson(SerializeDocumentToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeMailToJson, self).__call__(*args, **kwargs)
        result[u'attachments'] = self.get_attachments()
        return result

    def get_attachments(self):
        attachments = self.context.get_attachments()
        for attachment in attachments:
            if attachment.get('extracted'):
                attachment['extracted_document_url'] = uuidToURL(
                    attachment.get('extracted_document_uid'))
        return attachments


class ExtractAttachments(Service):

    def reply(self):
        if not self.context.can_extract_attachments_to_parent():
            raise NotReportedForbidden(mail_mf(
                'attachment_extraction_disallowed',
                default=u'You are not allowed to extract attachments from this Email'))

        # Disable CSRF protection, as POST requests cannot include the needed
        # X-CSRF-TOKEN to pass plone's autoprotect.
        alsoProvides(self.request, IDisableCSRFProtection)
        data = json_body(self.request)

        if 'positions' in data:
            positions = data.get('positions')
        else:
            positions = [attachment['position'] for attachment in
                         self.context.get_attachments(unextracted_only=True)]

        try:
            docs = self.context.extract_attachments_into_parent(positions)
        except (AlreadyExtractedError, InvalidAttachmentPosition) as exc:
            self.request.response.setStatus(400)
            return dict(error=dict(type="BadRequest", message=str(exc)))

        result = []
        for position, doc in docs.items():
            result.append({'position': position,
                           'extracted_document_url': doc.absolute_url(),
                           'extracted_document_title': doc.Title()})
        return result
