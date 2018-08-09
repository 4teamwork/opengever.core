from ftw.mail.mail import IMail
from opengever.base.transforms.msg2mime import Msg2MimeTransform
from opengever.mail.mail import initalize_title
from opengever.mail.mail import initialize_metadata
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.component import queryMultiAdapter
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

        if 'message' in data:
            field = IMail['message']
            deserializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldDeserializer)
            message = deserializer(data['message'])

            if message and message.filename.lower().endswith('.msg'):
                self.context.original_message = message
                transform = Msg2MimeTransform()
                eml = transform.transform(message.data)
                data['message'] = {
                    'data': eml,
                    'content-type': 'message/rfc822',
                    'filename': message.filename[:-3] + 'eml',
                }

        context = super(DeserializeMailFromJson, self).__call__(
            validate_all=validate_all, data=data, create=create)

        if create and 'message' in data:
            if not data.get('title'):
                context._update_title_from_message_subject()
                initalize_title(context, None)

            initialize_metadata(context, None)

        return context
