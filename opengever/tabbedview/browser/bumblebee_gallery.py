from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee import set_preferred_listing_view
from opengever.bumblebee.browser.preview_listing import PreviewListing
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

    @property
    def previews(self):
        """The previews listing is traversable for fetching content.
        """
        return (PreviewListing(self)
                .for_brains(self.get_brains())
                .with_batchsize(self.pagesize)
                .with_fetch_url(self.get_fetch_url()))

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

        doc_pointer = int(self.request.get('documentPointer', 0))
        if doc_pointer > 0:
            page_number = doc_pointer / self.table_source.config.pagesize
            self.table_source.config.batching_current_page = page_number + 1

        return self.table_source.search_results(query)

    def fetch(self):
        """Endpoint for retrieving more events with AJAX.
        """
        return self.previews.fetch()

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
