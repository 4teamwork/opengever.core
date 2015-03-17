from Acquisition import aq_base
from Acquisition import aq_inner
from collective.quickupload.browser.quick_upload import getDataFromAllRequests
from collective.quickupload.browser.quick_upload import QuickUploadFile
from collective.quickupload.browser.quick_upload import QuickUploadInit
from collective.quickupload.browser.quick_upload import QuickUploadView
from collective.quickupload.interfaces import IQuickUploadFileFactory
from five import grok
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base.transforms.msg2mime import Msg2MimeTransform
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.dexterity.utils import iterSchemata
from plone.protect import createToken
from plone.protect.interfaces import IDisableCSRFProtection
from plone.rfc822.interfaces import IPrimaryField
from plone.rfc822.interfaces import IPrimaryFieldInfo
from z3c.form.interfaces import IValue
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder
import mimetypes
import os



class OGQuickUploadInit(QuickUploadInit):
    """collective.quickupload uses the session, causing GET requests to
    make writes to the database which is prohibited by plone.protect.
    We must disable plone.protect.
    """

    def upload_settings(self, *args, **kwargs):
        alsoProvides(self.request, IDisableCSRFProtection)
        return super(OGQuickUploadInit, self).upload_settings(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        ori_js = super(OGQuickUploadInit, self).__call__(*args, **kwargs)
        og_js = 'xhr_{ul_id}.setParams({{"_authenticator": "{token}"}});'.format(
            ul_id=self.uploader_id,
            token=createToken())
        return '\n'.join((ori_js, og_js))


class OGQuickUploadView(QuickUploadView):
    """collective.quickupload uses the session, causing GET requests to
    make writes to the database which is prohibited by plone.protect.
    We must disable plone.protect.
    """

    def header_upload(self, *args, **kwargs):
        alsoProvides(self.request, IDisableCSRFProtection)
        return super(OGQuickUploadView, self).header_upload(*args, **kwargs)


class OGQuickUploadFile(QuickUploadFile):
    """When uploading a file with XHR, we have an empty request.form even
    when request params are submitted.
    For CSRF protection to work, we need to update the _authenticator in the form.
    """

    def quick_upload_file(self):
        token = getDataFromAllRequests(self.request, '_authenticator')
        if token:
            self.request.form['_authenticator'] = token

        result = super(OGQuickUploadFile, self).quick_upload_file()
        self.request.response.setHeader('Content-Type', 'application/json')
        return result


class OGQuickUploadCapableFileFactory(grok.Adapter):
    """OG specific Quick upload Adatper"""

    grok.context(ITabbedviewUploadable)
    grok.implements(IQuickUploadFileFactory)

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self,
                 filename,
                 title,
                 description,
                 content_type,
                 data, portal_type):

        if filename.lower().endswith('msg'):
            # its a outlook msg file
            # needs to be converted by the Msg2MimeTransform
            data = Msg2MimeTransform()(data)
            filename = filename.replace('msg', 'eml')

        portal_type = self.get_portal_type(filename)
        content = createContent(portal_type, title=filename)

        # Temporarily acquisition wrap content to make adaptation work
        content = content.__of__(self.context)

        self.set_primary_field_value(filename, data, content)
        self.set_default_values(content, self.context)

        # fire ObjectCreatedEvent (again) to trigger
        # sync_title_and_filename_handler
        notify(ObjectCreatedEvent(content))

        # Remove temporary acquisition wrapper
        content = aq_base(content)

        obj = addContentToContainer(self.context,
                                    content,
                                    checkConstraints=True)

        # rest of initialization
        notify(ObjectModifiedEvent(obj))

        obj.reindexObject()

        result = {}
        result['success'] = obj

        return result

    def set_primary_field_value(self, filename, data, obj):
        # filename must be unicode
        if not isinstance(filename, unicode):
            filename = filename.decode('utf-8')

        field = IPrimaryFieldInfo(obj).field
        value = field._type(data=data, filename=filename)
        field.set(field.interface(obj), value)

    def set_default_values(self, content, container):
        # set default values for all fields
        for schema in iterSchemata(content):
            for name, field in getFieldsInOrder(schema):
                if IPrimaryField.providedBy(field):
                    continue
                else:
                    default = queryMultiAdapter((
                        container,
                        container.REQUEST,
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
                    field.set(field.interface(content), value)

    def get_portal_type(self, filename):
        # check if its a mail object then create a ftw.mail
        # otherwise create a og.document
        if self._get_mimetype(filename) == 'message/rfc822':
            return 'ftw.mail.mail'
        else:
            return 'opengever.document.document'

    def _get_mimetype(self, filename):
        basepath, extension = os.path.splitext(filename)
        return mimetypes.types_map.get(extension)
