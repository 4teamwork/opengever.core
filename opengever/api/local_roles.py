from AccessControl.interfaces import IRoleManager
from opengever.base.interfaces import IOpengeverBaseLayer
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.local_roles import SerializeLocalRolesToJson
from zope.component import adapter
from zope.interface import implementer


@adapter(IRoleManager, IOpengeverBaseLayer)
@implementer(ISerializeToJson)
class GeverSerializeLocalRolesToJson(SerializeLocalRolesToJson):
    """The default local-roles serializer returns all current local roles
    by default. If we pass a search-param, it will return all available
    entries which could possibly be added to the local roles. This result
    set can contain a lot of entries.

    The GEVER-customization of this serializer returns a batched result-set
    if searching for entries but returns an unbatched result-set
    if just requesting the current local roles.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, search=None):
        results = super(GeverSerializeLocalRolesToJson, self).__call__(search)

        entries = results.get('entries', [])

        if search is not None:
            # The structure for batched results is to have a key called
            # 'items' which contains the results, not 'entries' as it comes from
            # the default implementation.
            batch = HypermediaBatch(self.request, results.pop('entries'))
            results['items'] = [entry for entry in batch]
            results['items_total'] = len(entries)
            if batch.links:
                results['batching'] = batch.links

        return results
