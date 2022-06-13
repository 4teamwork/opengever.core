from opengever.base.transforms.msg2mime import Msg2MimeTransform
from os.path import splitext
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from Products.CMFPlone.utils import safe_unicode


class BaseObjectCreatorCommand(object):
    """Base class to create an object in a container.
    """
    portal_type = None

    def __init__(self, context, title, **kwargs):
        self.context = context
        self.title = safe_unicode(title)
        self.additional_args = kwargs

    def execute(self):
        return createContentInContainer(
            self.context,
            self.portal_type,
            title=self.title,
            **self.additional_args)


class CreateDocumentCommand(BaseObjectCreatorCommand):
    """Create a new opengever.document.document object and update its fields
    with default values.

    """
    portal_type = 'opengever.document.document'
    primary_field_name = 'file'

    def __init__(self, context, filename, data, title=None, content_type='',
                 **kwargs):
        super(CreateDocumentCommand, self).__init__(context, title, **kwargs)
        self.set_file(filename, data, content_type)

    def set_file(self, filename, data, content_type):
        if not data:
            return

        # filename must be unicode
        if not isinstance(filename, unicode):
            filename = filename.decode('utf-8')

        self.additional_args.update({
            self.primary_field_name: NamedBlobFile(
                data=data, filename=filename, contentType=content_type)
        })


class CreateEmailCommand(CreateDocumentCommand):
    """Create a new ftw.mail.mail object.

    Also convert *.msg messages to *.eml, if necessary.

    """
    portal_type = 'ftw.mail.mail'
    primary_field_name = 'message'

    def __init__(self, context, filename, data, title=None, content_type='',
                 transform=None, **kwargs):
        self.transform = transform or Msg2MimeTransform()

        if self.is_msg_upload(filename):
            kwargs['original_message'] = NamedBlobFile(
                data=data, filename=safe_unicode(filename),
                contentType=content_type)
            filename, data = self.convert_to_mime(filename, data)

        super(CreateEmailCommand, self).__init__(
            context, filename, data, title, content_type, **kwargs)

    def is_msg_upload(self, filename):
        root, ext = splitext(filename)
        return ext.lower() == '.msg'

    def convert_to_mime(self, filename, data):
        data = self.transform.transform(data)
        filename = safe_unicode(filename)
        base_filename, ext = splitext(filename)
        filename = u'{}.eml'.format(base_filename)
        return filename, data

    def execute(self):
        obj = super(CreateEmailCommand, self).execute()
        obj._update_title_from_message_subject()

        return obj
