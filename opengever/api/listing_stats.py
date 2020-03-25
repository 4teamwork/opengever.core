from opengever.base.interfaces import IOpengeverBaseLayer
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class ListingStats(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'listing-stats': {
                '@id': '{}/@listing-stats'.format(self.context.absolute_url()),
            },
        }

        if not expand:
            return result

        result['listing-stats']['facet_pivot'] = {}  # Not implemented yet

        return result


class ListingStatsGet(Service):
    """API Endpoint which returns a solr facet_pivot for listings.

    GET folder-1/@listing-stats HTTP/1.1
    """

    def reply(self):
        stats = ListingStats(self.context, self.request)
        return stats(expand=True)['listing-stats']
