from ftw.bumblebee.config import PROCESSING_QUEUE
from ftw.bumblebee.interfaces import IBumblebeeServiceV3
from logging import getLogger
from opengever.base.handlebars import get_handlebars_template
from opengever.base.utils import disable_edit_bar
from opengever.document.versioner import Versioner
from opengever.document import _
from pkg_resources import resource_filename
from plone import api
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from uuid import uuid4
from zExceptions import BadRequest
from zope.annotation import IAnnotations
from zope.globalrequest import getRequest
from zope.i18n import translate
import json

logger = getLogger('opengever.document')

PDF_SAVE_TOKEN_KEY = 'opengever.document.save_pdf_under_token'
PDF_SAVE_SOURCE_UUID_KEY = 'opengever.document.save_pdf_under_source_uuid'
PDF_SAVE_SOURCE_VERSION_KEY = 'opengever.document.save_pdf_under_source_version'
PDF_SAVE_STATUS_KEY = 'opengever.document.save_pdf_under_status'
PDF_SAVE_OWNER_ID_KEY = 'opengever.document.save_pdf_document_owner_id'


class SavePDFDocumentUnder(BrowserView):
    """Display a view to indicate the status of the pdf generation"""

    template = ViewPageTemplateFile("templates/save_pdf_under.pt")

    def __init__(self, context, request):
        super(SavePDFDocumentUnder, self).__init__(context, request)

    def __call__(self):
        disable_edit_bar()

        annotations = IAnnotations(self.context)
        self.source_document = uuidToObject(annotations.get(PDF_SAVE_SOURCE_UUID_KEY))
        self.version_id = annotations.get(PDF_SAVE_SOURCE_VERSION_KEY)
        self.destination_document = self.context
        self.destination = self.context.get_parent_dossier()
        self.trigger_conversion()
        return self.template()

    def get_callback_url(self):
        return "{}/save_pdf_under_callback".format(
            self.destination_document.absolute_url())

    def trigger_conversion(self):
        token = str(uuid4())
        annotations = IAnnotations(self.destination_document)
        annotations[PDF_SAVE_TOKEN_KEY] = token
        annotations[PDF_SAVE_OWNER_ID_KEY] = api.user.get_current().getId()

        if self.version_id is not None:
            document = Versioner(self.source_document).retrieve(self.version_id)
        else:
            document = self.source_document

        if IBumblebeeServiceV3(getRequest()).queue_demand(
                document, PROCESSING_QUEUE, self.get_callback_url(), opaque_id=token):
            annotations[PDF_SAVE_STATUS_KEY] = "conversion-demanded"
        else:
            raise BadRequest("This document is not convertable.")

    @property
    def vuejs_template(self):
        return get_handlebars_template(
            resource_filename('opengever.document.browser',
                              'templates/save_pdf_under.html'))

    def get_save_pdf_title(self):
        return _(u'title_save_pdf',
                 default=u'Save PDF of ${title} under ${destination}',
                 mapping={'title': self.source_document.title,
                          'destination': self.destination.title})

    def translations(self):
        return json.dumps({
            'msg_pdf_generation_succesfull': translate(
                _(u'msg_pdf_generation_succesfull', default=u'PDF generated successfully'),
                context=self.request),
            'msg_pdf_generation_error': translate(
                _(u'msg_pdf_generation_error', default=u'PDF generation error'),
                context=self.request),
            'msg_pdf_generation_in_progress': translate(
                _(u'msg_pdf_generation_in_progress', default=u'PDF is being generated'),
                context=self.request),
            'msg_pdf_generation_failed': translate(
                _(u'msg_pdf_generation_failed', default=u'PDF generation failed'),
                context=self.request),
            'msg_pdf_generation_timeout': translate(
                _(u'msg_pdf_generation_timeout', default=u'PDF generation timed out'),
                context=self.request),
            'label_button_destination_document': translate(
                _(u'label_button_destination_document', default=u'Go to destination document'),
                context=self.request),
            'label_button_error': translate(
                _(u'label_button_error', default=u'Error'),
                context=self.request),
            'label_button_creation_in_progress': translate(
                _(u'label_button_creation_in_progress', default=u'Generating'),
                context=self.request),
            'label_backlink_to_source_document': translate(
                _(u'label_backlink_to_source_document', default=u'Back to source document'),
                context=self.request),
            'label_error': translate(
                _(u'label_error', default=u'Error'),
                context=self.request),
            })

    def destination_document_url(self):
        return self.destination_document.absolute_url()

    def source_document_url(self):
        return self.source_document.absolute_url()

    def get_conversion_status_url(self):
        return "{}/get_conversion_status".format(self.destination_document.absolute_url())


class DocumentConversionStatusView(BrowserView):

    def __call__(self):
        status = IAnnotations(self.context).get(PDF_SAVE_STATUS_KEY)
        return json.dumps({"conversion-status": status})
