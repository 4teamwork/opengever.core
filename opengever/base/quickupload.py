from Acquisition import aq_inner
from collective.quickupload.browser.interfaces import IQuickUploadFileFactory
from five import grok
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.document.document import IDocumentSchema
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.rfc822.interfaces import IPrimaryField
from z3c.form.interfaces import IValue
from zope import schema
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder
import mimetypes


class OGQuickUploadCapableFileFactory (grok.Adapter):
    """OG specific Quick upload Adatper"""

    grok.context(ITabbedviewUploadable)
    grok.implements(IQuickUploadFileFactory)

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(
        self, filename, title, description, content_type, data, portal_type):

        #create Namedfile
        mimetype = mimetypes.types_map[
                filename[filename.rfind('.'):].lower()]

        # check if its a mail object then create a ftw.mail
        # otherwise create a og.document

        if mimetype == 'message/rfc822':
            portal_type = 'ftw.mail.mail'
        else:
            portal_type = 'opengever.document.document'

        result = {}

        fields = dict(schema.getFieldsInOrder(IDocumentSchema))

        # filename must be unicode
        if not isinstance(filename, unicode):
            filename = filename.decode('utf-8')

        fileObj = fields['file']._type(
            data=data, contentType=mimetype, filename=filename)

        obj = createContentInContainer(
            self.context, portal_type)

        # set default values for all fields
        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):

                if IPrimaryField.providedBy(field):
                    field.set(field.interface(obj), fileObj)
                else:
                    default = queryMultiAdapter((
                            obj,
                            obj.REQUEST,
                            None,
                            field,
                            None,
                            ), IValue, name='default')
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
                    field.set(field.interface(obj), value)

        notify(ObjectModifiedEvent(obj))

        obj.reindexObject()

        result['success'] = obj
        return result
