from five import grok
from ftw.bumblebee.utils import get_representation_url_by_brain
from opengever.base.browser.helper import get_css_class
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.tabbedview.browser.tabs import Documents
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound
from zope.interface import Interface


class BumblebeeGallery(Documents):
    grok.name('tabbedview_view-galleryview')
    grok.require('zope2.View')
    grok.context(Interface)

    template = ViewPageTemplateFile('bumblebeegallery.pt')
    previews_template = ViewPageTemplateFile('bumblebee_previews.pt')

    document_list_name = 'documents'

    amount_preloaded_documents = 24

    def __call__(self, *args, **kwargs):
        if not is_bumblebee_feature_enabled():
            raise NotFound
        return self.template()

    def _query(self, **kwargs):
        query = dict(
            object_provides='ftw.bumblebee.interfaces.IBumblebeeable',
            sort_on='modified',
            sort_order="descending",
            path='/'.join(self.context.getPhysicalPath()))

        if 'searchable_text' in self.request.keys() and \
           self.request['searchable_text'] != '':
            query['SearchableText'] = self.request.get('searchable_text')
            if not query['SearchableText'].endswith('*'):
                query['SearchableText'] += '*'

        query.update(kwargs)
        return query

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
                'document_id': document_id,
                'css_class': get_css_class(brain),
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
