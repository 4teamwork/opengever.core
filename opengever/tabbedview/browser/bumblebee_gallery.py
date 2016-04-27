from five import grok
from ftw.bumblebee.utils import get_representation_url_by_brain
from opengever.base.browser.helper import get_css_class
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.tabbedview.browser.tabs import Documents
from opengever.tabbedview.browser.personal_overview import MyDocuments
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound


class BumblebeeGalleryMixin(object):

    template = ViewPageTemplateFile('bumblebee_gallery.pt')
    previews_template = ViewPageTemplateFile('bumblebee_previews.pt')

    amount_preloaded_documents = 21

    def __call__(self, *args, **kwargs):
        if not is_bumblebee_feature_enabled():
            raise NotFound
        return self.template()

    @property
    def list_view_name(self):
        return self.view_name.split('-gallery')[0]

    def _query(self, **kwargs):
        return self.table_source.build_query()

    def previews(self, **kwargs):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(self._query())

        next_document_id = int(self.request.get('next_document_id', 0))
        to_document_id = next_document_id + self.amount_preloaded_documents

        for document_id, brain in enumerate(
                brains[next_document_id:to_document_id],
                start=next_document_id):

            desc = brain.Description
            if desc:
                desc = len(desc) < 50 and desc or desc[:49] + '...'

            yield {
                'title': brain.Title,
                'description': desc,
                'overlay_url': brain.getURL() + '/file-preview',
                'preview_image_url': get_representation_url_by_brain(
                    'thumbnail', brain),
                'uid': brain.UID,
                'mime_type_css_class': get_css_class(brain),
            }

    def available(self):
        return self.number_of_documents() > 0

    def number_of_documents(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return len(catalog(self._query()))

    def fetch(self):
        """Action for retrieving more events (based on `next_event_id` in
        the request) with AJAX.
        """
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        # The HTML stripped in order to have empty response content when
        # there are no tags at all, so that diazo does not try to
        # parse it.
        return self.previews_template().strip()


class DocumentsGallery(BumblebeeGalleryMixin, Documents):
    grok.name('tabbedview_view-documents-gallery')


class MyDocumentsGallery(BumblebeeGalleryMixin, MyDocuments):
    grok.name('tabbedview_view-mydocuments-gallery')
