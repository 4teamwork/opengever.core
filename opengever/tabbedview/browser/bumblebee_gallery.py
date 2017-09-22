from ftw import bumblebee
from opengever.base.browser.helper import get_css_class
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee import set_preferred_listing_view
from opengever.tabbedview.browser.personal_overview import MyDocuments
from opengever.tabbedview.browser.tabs import Documents
from opengever.tabbedview.browser.tabs import Trash
from opengever.task.browser.related_documents import RelatedDocuments
from plone.memoize.view import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound
import re


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
        return self._extract_base_view_name(self.__name__)

    def get_fetch_url(self):
        return '{}/{}/fetch'.format(self.context.absolute_url(), self.__name__)

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

        query = self.table_source.build_query()

        # When https://github.com/4teamwork/opengever.core/pull/3399 is fixed,
        # set the default ordering on the table source config instead.
        if isinstance(query, dict) and 'sort_on' not in query:
            query['sort_on'] = 'modified'
            query['sort_order'] = 'descending'
        return self.table_source.search_results(query)

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

    def _extract_base_view_name(self, view_name):
        """Extracts the base-view-name without tabbedview_view- and -gallery.
        """
        result = re.search("tabbedview_view-(.*?)-gallery", view_name)
        return result.group(1) if result else view_name


class DocumentsGallery(BumblebeeGalleryMixin, Documents):
    """
    """


class MyDocumentsGallery(BumblebeeGalleryMixin, MyDocuments):
    """
    """


class TrashGallery(BumblebeeGalleryMixin, Trash):
    """
    """


class RelatedDocumentsGallery(BumblebeeGalleryMixin, RelatedDocuments):
    """
    """
