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
        return self.template()

    @property
    def list_view_name(self):
        return self.view_name.split('-gallery')[0]

    def available(self):
        return self.number_of_documents() > 0

    def number_of_documents(self):
        return len(self._get_brains())

    def previews(self, **kwargs):
        brains = self._get_brains()

        # TODO: Batching
        for brain in brains:
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

    def _get_brains(self):
        if not hasattr(self, '_brains'):
            catalog = getToolByName(self.context, 'portal_catalog')
            setattr(self, '_brains', catalog(self.table_source.build_query()))
        return getattr(self, '_brains')


class DocumentsGallery(BumblebeeGalleryMixin, Documents):
    grok.name('tabbedview_view-documents-gallery')


class MyDocumentsGallery(BumblebeeGalleryMixin, MyDocuments):
    grok.name('tabbedview_view-mydocuments-gallery')
