from opengever.base import _
from opengever.base.utils import NullObject


def title_helper(item, title):
    if isinstance(item, NullObject):
        return _(u'label_null', default=u'Null')
    else:
        return title
