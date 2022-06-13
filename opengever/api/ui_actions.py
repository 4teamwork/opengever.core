from opengever.base.interfaces import IContextActions
from opengever.base.interfaces import IListingActions
from opengever.webactions.renderer import WebActionsSafeDataGetter
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zope.component import queryMultiAdapter


class UIActionsGet(Service):

    def extract_params(self):
        params = self.request.form.copy()

        categories = params.get("categories", [])
        if not isinstance(categories, list):
            categories = [categories]
        listings = params.get("listings", [])
        if not isinstance(listings, list):
            listings = [listings]

        return categories, listings

    def _get_listing_actions(self, name):
        adapter = queryMultiAdapter((self.context, self.request),
                                    interface=IListingActions,
                                    name=name)
        return adapter.get_actions() if adapter else []

    def serialize_actions(self, actions):
        return [{'id': action} for action in actions]

    def extend_with_context_actions(self, response):
        adapter = queryMultiAdapter((self.context, self.request),
                                    interface=IContextActions)
        context_actions = adapter.get_actions() if adapter else []
        response['context_actions'] = self.serialize_actions(context_actions)

    def extend_with_listing_actions(self, response, listings):
        all_actions = [self._get_listing_actions(listing) for listing in listings]
        intersection = set(*all_actions[:1]).intersection(*all_actions[1:])
        if intersection:
            sorted_actions = [action for action in all_actions[0] if action in intersection]
            response['listing_actions'] = self.serialize_actions(sorted_actions)
        else:
            response['listing_actions'] = []

    def extend_with_webactions(self, response):
        data_getter = WebActionsSafeDataGetter(self.context, self.request, None)
        webactions = data_getter.get_webactions_data(flat=True)
        response['webactions'] = json_compatible(webactions)

    def reply(self):
        categories, listings = self.extract_params()
        url = self.request['ACTUAL_URL']
        qs = self.request['QUERY_STRING']
        if qs:
            url = '?'.join((url, qs))
        response = {'@id': url}
        if 'context_actions' in categories:
            self.extend_with_context_actions(response)
        if 'listing_actions' in categories:
            self.extend_with_listing_actions(response, listings)
        if 'webactions' in categories:
            self.extend_with_webactions(response)
        return response
