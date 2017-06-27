from Products.CMFPlone.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
from ftw import bumblebee
from opengever.base.browser.helper import get_css_class
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee import set_preferred_listing_view
from opengever.tabbedview.browser.personal_overview import MyDocuments
from opengever.tabbedview.browser.tabs import Documents
from opengever.tabbedview.browser.tabs import Trash
from opengever.task.browser.related_documents import RelatedDocuments
from plone.memoize.view import memoize
from zExceptions import NotFound


class BumblebeeGalleryMixin(object):
    """This mixin provides the functionality to render the
    bumblebee gallery view in a tab.
    """

    template = ViewPageTemplateFile('bumblebee_gallery.pt')
    previews_template = ViewPageTemplateFile('bumblebee_previews.pt')

    object_provides = 'ftw.bumblebee.interfaces.IBumblebeeable'

    def __call__(self, *args, **kwargs):
        if not is_bumblebee_feature_enabled():
            raise NotFound

        set_preferred_listing_view('gallery')

        return self.template()

    @property
    def list_view_name(self):
        raise NotImplementedError

    def get_fetch_url(self):
        return '{}/{}-fetch'.format(self.context.absolute_url(), self.__name__)

    def available(self):
        return self.number_of_documents() > 0

    def number_of_documents(self):
        return len(self.get_brains())

    def previews(self, **kwargs):
        brains = self.get_brains()

        from_batch_id = int(self.request.get('documentPointer', 0))
        to_batch_id = from_batch_id + self.pagesize

        for brain in brains[from_batch_id:to_batch_id]:
            yield {
                'title': brain.Title,
                'overlay_url': '{}/@@bumblebee-overlay-listing'.format(brain.getURL()),
                'preview_image_url': bumblebee.get_service_v3().get_representation_url(
                    brain, 'thumbnail'),
                'uid': brain.UID,
                'mime_type_css_class': get_css_class(brain),
            }

    @memoize
    def get_brains(self):
        self.table_source.config.filter_text = self.request.get(
            'searchable_text', '')

        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(self.table_source.build_query())

    def fetch(self):
        """Action for retrieving more events (based on `next_event_id` in
        the request) with AJAX.
        """
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        # The HTML stripped in order to have empty response content when
        # there are no tags at all, so that diazo does not try to
        # parse it.
        if int(self.request.get('documentPointer', 0)) >= self.number_of_documents():
            # We have to return an empty string if we have no more documents
            # to render. Otherwise plone.protect will log a error-warning:
            # WARNING plone.protect error parsing dom, failure to add csrf
            # token to response
            return ''
        return self.previews_template().strip()


class DocumentsGallery(BumblebeeGalleryMixin, Documents):
    grok.name('tabbedview_view-documents-gallery')

    @property
    def list_view_name(self):
        return "documents"


class DocumentsGalleryFetch(DocumentsGallery):
    """Returns the next gallery-items.

    Unfortunately it's not possible to use a traversable method with
    five.grok-views. Therefore we have to register an own browserview
    to fetch the next gallery-items.

    This browserview can be removed and implemented with allowed-attributes as
    soon as the parent views are registered as Zope 3 BrowserViews.
    """
    grok.name('tabbedview_view-documents-gallery-fetch')

    def __call__(self):
        return self.fetch()


class MyDocumentsGallery(BumblebeeGalleryMixin, MyDocuments):
    grok.name('tabbedview_view-mydocuments-gallery')

    @property
    def list_view_name(self):
        return "mydocuments"


class MyDocumentsGalleryFetch(MyDocumentsGallery):
    """Returns the next gallery-items.

    Unfortunately it's not possible to use a traversable method with
    five.grok-views. Therefore we have to register an own browserview
    to fetch the next gallery-items.

    This browserview can be removed and implemented with allowed-attributes as
    soon as the parent views are registered as Zope 3 BrowserViews.
    """
    grok.name('tabbedview_view-mydocuments-gallery-fetch')

    def __call__(self):
        return self.fetch()


class TrashGallery(BumblebeeGalleryMixin, Trash):
    grok.name('tabbedview_view-trash-gallery')

    @property
    def list_view_name(self):
        return "trash"


class TrashGalleryFetch(TrashGallery):
    """Returns the next gallery-items.

    Unfortunately it's not possible to use a traversable method with
    five.grok-views. Therefore we have to register an own browserview
    to fetch the next gallery-items.

    This browserview can be removed and implemented with allowed-attributes as
    soon as the parent views are registered as Zope 3 BrowserViews.
    """
    grok.name('tabbedview_view-trash-gallery-fetch')

    def __call__(self):
        return self.fetch()


class RelatedDocumentsGallery(BumblebeeGalleryMixin, RelatedDocuments):
    grok.name('tabbedview_view-relateddocuments-gallery')

    @property
    def list_view_name(self):
        return "relateddocuments"

    @memoize
    def get_brains(self):
        # The build_query of the RelatedDocuments-View returns the brains instead
        # a query object. So we have to override the get_brains-function to
        # handle this exception
        self.table_source.config.filter_text = self.request.get(
            'searchable_text', '')

        return self.table_source.build_query()


class RelatedDocumentsGalleryFetch(RelatedDocumentsGallery):
    """Returns the next gallery-items.

    Unfortunately it's not possible to use a traversable method with
    five.grok-views. Therefore we have to register an own browserview
    to fetch the next gallery-items.

    This browserview can be removed and implemented with allowed-attributes as
    soon as the parent views are registered as Zope 3 BrowserViews.
    """
    grok.name('tabbedview_view-relateddocuments-gallery-fetch')

    def __call__(self):
        return self.fetch()
