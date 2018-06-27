from opengever.ogds.base.actor import Actor
from plone.memoize import ram


def display_name_cache_key(func, userid):
    return userid


@ram.cache(display_name_cache_key)
def display_name(userid):
    if not isinstance(userid, unicode):
        if userid is not None:
            userid = userid.decode('utf-8')
        else:
            userid = ''

    return Actor.user(userid).get_label()
