from opengever.ogds.base.utils import get_client_id

def client_cache_key(fun, *args, **kwargs):
    """`plone.memoize.volatile` cache key which caches per client.
    """
    return get_client_id()
