from Acquisition import aq_inner
from collective.quickupload.browser.quick_upload import getDataFromAllRequests
from collective.quickupload.browser.quick_upload import QuickUploadFile
from collective.quickupload.browser.quick_upload import QuickUploadInit
from collective.quickupload.browser.quick_upload import QuickUploadView
from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base.command import CreateDocumentCommand
from opengever.base.command import CreateEmailCommand
from opengever.document.behaviors import IBaseDocument
from opengever.mail.mail import MESSAGE_SOURCE_DRAG_DROP_UPLOAD
from opengever.quota.exceptions import ForbiddenByQuota
from plone.protect import createToken
from plone.protect.interfaces import IDisableCSRFProtection
from zope.component import adapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Invalid
from zope.lifecycleevent import ObjectModifiedEvent
import json
import mimetypes
import os
import transaction


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

        try:
            result = super(OGQuickUploadFile, self).quick_upload_file()
            self.request.response.setHeader('Content-Type', 'application/json')

            parsed_result = json.loads(result)
            if parsed_result.get('success'):
                # We're updating a document-ish in-place
                if IBaseDocument.providedBy(self.context):
                    notify(ObjectModifiedEvent(self.context))

        except Invalid as exc:
            # The error response aborts the transaction for us
            msg = translate(exc.message, context=self.context.REQUEST)
            return self._error_response(msg)

        return result


@implementer(IQuickUploadFileFactory)
@adapter(ITabbedviewUploadable)
class OGQuickUploadCapableFileFactory(object):
    """OG specific Quick upload Adatper"""

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, filename, title, description, content_type,
                 data, portal_type):
        """Quickupload description inputs are hidden in gever
        therefore we skip the description.
        """
        if self.is_email_upload(filename):
            command = CreateEmailCommand(
                self.context, filename, data,
                message_source=MESSAGE_SOURCE_DRAG_DROP_UPLOAD)
        else:
            command = CreateDocumentCommand(self.context, filename, data)

        try:
            obj = command.execute()
        except ForbiddenByQuota as exc:
            # This is an error, we abort the transaction
            transaction.abort()
            msg = translate(exc.message, context=self.context.REQUEST)
            return {'error': msg, 'success': None}
        except Invalid as exc:
            # This is an error, we abort the transaction
            transaction.abort()
            msg = translate(exc.message, context=self.context.REQUEST)
            return {'error': msg, 'success': None}

        result = {'success': obj}
        return result

    def is_email_upload(self, filename):
        extension = os.path.splitext(filename)[1].lower()
        mimetype = self._get_mimetype(extension)
        return extension == '.msg' or mimetype == 'message/rfc822'

    def _get_mimetype(self, extension):
        return mimetypes.types_map.get(extension)
