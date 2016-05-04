from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.bumblebee import get_representation_url_by_brain
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee import set_prefered_listing_view
from opengever.tabbedview.browser.personal_overview import MyDocuments
from opengever.tabbedview.browser.tabs import Documents
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound


class BumblebeeGalleryMixin(object):
    """This mixin provides the functionality to render the
    bumblebee gallery view in a tab.
    """

    template = ViewPageTemplateFile('bumblebee_gallery.pt')
    previews_template = ViewPageTemplateFile('bumblebee_previews.pt')

    amount_preloaded_documents = 24

    object_provides = 'ftw.bumblebee.interfaces.IBumblebeeable'

    def __call__(self, *args, **kwargs):
        if not is_bumblebee_feature_enabled():
            raise NotFound

        set_prefered_listing_view('gallery')
        return self.template()

    @property
    def list_view_name(self):
        return self.view_name.split('-gallery')[0]

    def available(self):
        return self.number_of_documents() > 0

    def number_of_documents(self):
        return len(self.get_brains())

    def previews(self, **kwargs):
        brains = self.get_brains()

        # TODO: Batching
        for brain in brains:
            yield {
                'title': brain.Title,
                'overlay_url': '{}/@@bumblebee-overlay-listing'.format(brain.getURL()),
                'preview_image_url': get_representation_url_by_brain(
                    'thumbnail', brain),
                'uid': brain.UID,
                'mime_type_css_class': get_css_class(brain),
            }

    def get_brains(self):
        if not hasattr(self, '_brains'):
            catalog = getToolByName(self.context, 'portal_catalog')
            setattr(self, '_brains', catalog(self.table_source.build_query()))
        return getattr(self, '_brains')


class DocumentsGallery(BumblebeeGalleryMixin, Documents):
    grok.name('tabbedview_view-documents-gallery')


class MyDocumentsGallery(BumblebeeGalleryMixin, MyDocuments):
    grok.name('tabbedview_view-mydocuments-gallery')
