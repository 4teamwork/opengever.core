from ftw import bumblebee
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.base.browser.helper import get_css_class
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PreviewListing(object):
    """The PreviewListing partial renders previews for a bunch of documents.

    Usage:
    - Instantiate with a view, in which this listing is rendered.
    - Use ``.for_objects`` or ``.for_brains`` for defining the documents to
      be displayed.
    - Configure the fetch url with ``.with_fetch_url()``, make sure that
      you setup allowed_attributes on your view when necessary.
    - Maybe configure the batchsize, when needed.
    """

    listing_template = ViewPageTemplateFile('templates/preview_listing.pt')
    previews_template = ViewPageTemplateFile('templates/previews.pt')

    def __init__(self, view):
        """Instantiate the preview listing with a view and a published accessor.
        The view should have a publishable attribute for accessing these previews.

        :param view: The browser view on whcih this listing is rendered.
        :type view: BrowserView
        """
        self.items = None
        self.fetch_url = None
        self.batchsize = 50
        # context and request is required for rendering page templates.
        self.context = view.context
        self.request = view.request

    def for_objects(self, objects):
        """Setup the preview listing with a list of Plone content objects.
        """
        self.items = PreviewListingObjects(objects)
        return self

    def for_brains(self, brains):
        """Setup the preview listing with a list of catalog brains.
        """
        self.items = PreviewListingBrains(brains)
        return self

    def with_fetch_url(self, fetch_url):
        """Configure the fetch url.
        """
        self.fetch_url = fetch_url
        return self

    def with_batchsize(self, batchsize):
        """Configure the batchsize.
        """
        self.batchsize = batchsize
        return self

    def render(self):
        """Render the items.
        """
        assert self.items is not None, \
            'No items configured; use .for_objects() or .for_brains().'
        assert self.fetch_url is not None, \
            'No fetch_url configured.'

        number_of_documents = self.items.get_number_of_documents()
        return self.listing_template(
            available=number_of_documents > 0,
            number_of_documents=number_of_documents,
            fetch_url=self.fetch_url,
            previews_html=self.render_batch(0))

    def render_batch(self, first):
        """Return the batch to be rendered.

        :param first: The index of the first item to return, 0-indexed.
        :type first: int
        """
        items = self.items.get_batch(first, self.batchsize)
        if items:
            return self.previews_template(
                previews=map(self.items.get_infos_for, items))
        else:
            # We have to return an empty string if we have no more documents
            # to render. Otherwise plone.protect will log a error-warning:
            # WARNING plone.protect error parsing dom, failure to add csrf
            # token to response.
            return ''

    def fetch(self):
        """Fetch the next batch.
        """
        next_batch_first_index = int(self.request.get('documentPointer', 0))
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.render_batch(next_batch_first_index)


class PreviewListingItems(object):
    """PreviewListingItems provides information about the items to be rendered.

    The PreviewListingItems is an abstract class, subclassed depending on the
    type of items it holds (plone objects, brains).
    The generic interface is used for providing rendering information about the
    items without the need to normalize the items (e.g. get the object for a
    brain).
    It is implemented so that it can be used in a lazy manner for beeing
    performance friendly.
    """

    def __init__(self, items):
        self.items = items

    def get_batch(self, first, max_amount):
        """Slices the current items for rendering a specific batch of items.
        The method may return a generator.
        The method may return less items than ``max_amount``.

        :param first: The index of the first item to return, 0-indexed.
        :type first: int
        :param max_amount: The maximum number of items ot return.
        :type maximum: int
        :returns: An iterable with 0 to maximum number of items.
        """
        return self.items[first:first + max_amount]

    def get_number_of_documents(self):
        """Return the total number of documents:

        :returns: Total number of documents.
        :rtype: int
        """
        return len(self.items)

    def get_infos_for(self, item):
        """Return the infos for this item as dictionary.
        """
        raise NotImplementedError()


class PreviewListingObjects(PreviewListingItems):

    def get_infos_for(self, obj):
        return {
            'title': obj.Title(),
            'overlay_url': obj.absolute_url() + '/@@bumblebee-overlay-listing',
            'uid': IUUID(obj),
            'checksum': IBumblebeeDocument(obj).get_checksum(),
            'mime_type_css_class': get_css_class(obj),
            'preview_image_url': bumblebee.get_service_v3().get_representation_url(
                obj, 'thumbnail')}


class PreviewListingBrains(PreviewListingItems):

    def get_infos_for(self, brain):
        return {
            'title': brain.Title,
            'overlay_url': brain.getURL() + '/@@bumblebee-overlay-listing',
            'uid': brain.UID,
            'checksum': brain.bumblebee_checksum,
            'mime_type_css_class': get_css_class(brain),
            'preview_image_url': bumblebee.get_service_v3().get_representation_url(
                brain, 'thumbnail')}
