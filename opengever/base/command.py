from Acquisition import aq_base
from opengever.base.transforms.msg2mime import Msg2MimeTransform
from os.path import join
from os.path import splitext
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.dexterity.utils import iterSchemata
from plone.rfc822.interfaces import IPrimaryField
from plone.rfc822.interfaces import IPrimaryFieldInfo
from z3c.form.interfaces import IValue
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder


class CreateDocumentCommand(object):
    """Create a new opengever.document.document object and update its fields
    with default values.

    """
    portal_type = 'opengever.document.document'
    skip_defaults_fields = []

    def __init__(self, context, filename, data):
        self.context = context
        self.data = data
        self.filename = filename
        self.title = filename

    def execute(self):
        content = createContent(self.portal_type, title=self.title)

        # Temporarily acquisition wrap content to make adaptation work
        content = content.__of__(self.context)
        self.set_primary_field_value(self.filename, self.data, content)
        self.set_default_values(content, self.context)
        self.notify_created(content)

        # Remove temporary acquisition wrapper
        content = aq_base(content)
        obj = addContentToContainer(self.context,
                                    content,
                                    checkConstraints=True)
        self.notify_modified(obj)

        obj.reindexObject()
        return obj

    def notify_created(self, content):
        """Fire ObjectCreatedEvent (again) to trigger
        sync_title_and_filename_handler.

        """
        notify(ObjectCreatedEvent(content))

    def notify_modified(self, content):
        """Trigger rest of initialization."""

        notify(ObjectModifiedEvent(content))

    def set_primary_field_value(self, filename, data, obj):
        # filename must be unicode
        if not isinstance(filename, unicode):
            filename = filename.decode('utf-8')

        field = IPrimaryFieldInfo(obj).field
        value = field._type(data=data, filename=filename)
        field.set(field.interface(obj), value)

    def set_default_values(self, content, container):
        """Set default values for all fields.

        This is necessary for content created programmatically since dexterity
        only sets default values in a view.

        """
        for schema in iterSchemata(content):
            for name, field in getFieldsInOrder(schema):
                if name in self.skip_defaults_fields:
                    continue
                if IPrimaryField.providedBy(field):
                    continue
                else:
                    default = queryMultiAdapter(
                        (container, container.REQUEST, None, field, None),
                        IValue, name='default')
                    if default is not None:
                        default = default.get()
                    if default is None:
                        default = getattr(field, 'default', None)
                    if default is None:
                        try:
                            default = field.missing_value
                        except AttributeError:
                            pass
                    value = default
                    field.set(field.interface(content), value)


class CreateEmailCommand(CreateDocumentCommand):
    """Create a new ftw.mail.mail object and update its fields
    with default values.

    Also convert *.msg messages to *.eml.

    """
    portal_type = 'ftw.mail.mail'

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
