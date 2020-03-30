from opengever.base import _
from opengever.base.utils import NullObject
from opengever.ogds.base.actor import Actor
from plone.memoize import ram


def title_helper(item, title):
    if isinstance(item, NullObject):
        return _(u'label_null', default=u'Null')
    else:
        return title


def display_name_cache_key(func, userid):
    return userid


@ram.cache(display_name_cache_key)
def display_name(userid):
    if not isinstance(userid, unicode):
        if userid is not None:
            userid = userid.decode('utf-8')
        else:
            userid = ''

    return Actor.lookup(userid).get_label(with_principal=False)
