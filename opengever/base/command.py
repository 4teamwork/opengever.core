from Acquisition import aq_base
from opengever.base.transforms.msg2mime import Msg2MimeTransform
from os.path import join
from os.path import splitext
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent


class BaseObjectCreatorCommand(object):
    """Base class to create an object in a container.
    """
    portal_type = None

    def __init__(self, context, title, **kwargs):
        self.context = context
        self.title = title
        self.additional_args = kwargs

    def execute(self):
        content = createContent(self.portal_type, title=self.title,
                                **self.additional_args)

        obj = addContentToContainer(
            self.context, content, checkConstraints=True)

        self.finish_creation(obj)

        obj.reindexObject()
        return obj

    def finish_creation(self, content):
        """Trigger rest of initialization."""

        notify(ObjectModifiedEvent(content))


class CreateDocumentCommand(BaseObjectCreatorCommand):
    """Create a new opengever.document.document object and update its fields
    with default values.

    """
    portal_type = 'opengever.document.document'

    def __init__(self, context, filename, data, title=None, content_type='',
                 **kwargs):
        super(CreateDocumentCommand, self).__init__(context, title, **kwargs)

        # filename must be unicode
        if not isinstance(filename, unicode):
            filename = filename.decode('utf-8')

        self.data = data
        self.filename = filename
        self.content_type = content_type

    def execute(self):
        content = createContent(self.portal_type, title=self.title,
                                **self.additional_args)

        # Temporarily acquisition wrap content to make adaptation work
        content = content.__of__(self.context)
        self.set_primary_field_value(content)
        self.notify_created(content)

        # Remove temporary acquisition wrapper
        content = aq_base(content)
        obj = addContentToContainer(self.context,
                                    content,
                                    checkConstraints=True)
        self.finish_creation(obj)

        obj.reindexObject()
        return obj

    def notify_created(self, content):
        """Fire ObjectCreatedEvent (again) to trigger
        sync_title_and_filename_handler.

        """
        notify(ObjectCreatedEvent(content))

    def set_primary_field_value(self, obj):
        if not self.data:
            return

        field = IPrimaryFieldInfo(obj).field
        value = field._type(data=self.data, filename=self.filename,
                            contentType=self.content_type)
        field.set(field.interface(obj), value)


class CreateEmailCommand(CreateDocumentCommand):
    """Create a new ftw.mail.mail object and update its fields
    with default values.

    Also convert *.msg messages to *.eml.

    """
    portal_type = 'ftw.mail.mail'

    def notify_created(self, content):
        """Make sure filename is updated from subject upon creation.
        """
        content._update_title_from_message_subject()
        notify(ObjectCreatedEvent(content))

    def is_msg_upload(self):
        root, ext = splitext(self.filename)
        return ext.lower() == '.msg'

    def convert_to_mime(self):
        data = Msg2MimeTransform().transform(self.data)
        root, ext = splitext(self.filename)
        filename = join(root, '.eml')
        return filename, data

    def execute(self):
        if self.is_msg_upload():
            self.filename, self.data = self.convert_to_mime()
        return super(CreateEmailCommand, self).execute()
