from ftw.mail.mail import IMail
from opengever.api.document import SerializeDocumentToJson
from opengever.base.transforms.msg2mime import Msg2MimeTransform
from opengever.mail.mail import initialize_metadata
from opengever.mail.mail import initialize_title
from plone.namedfile.file import NamedBlobFile
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


# Convert .msg files to .eml and store the .msg in the 'original_message'
# field.
@implementer(IDeserializeFromJson)
@adapter(IMail, Interface)
class DeserializeMailFromJson(DeserializeFromJson):

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
        result[u'attachments'] = self.context.get_attachments()
        return result
