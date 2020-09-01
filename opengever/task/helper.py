from opengever.inbox import FORWARDING_TASK_TYPE_ID
from opengever.task.util import getTaskTypeVocabulary
from plone.api.portal import get_current_language
from plone.memoize import ram
from zope.component.hooks import getSite
from zope.globalrequest import getRequest


@ram.cache(lambda m, i, value: '{}-{}'.format(value, get_current_language()))
def task_type_helper(item, value):
    """Translate the task type with the vdex vocabulary, which provides
    its own translations stored in the vdex files.
    """
    portal = getSite()
    if value == FORWARDING_TASK_TYPE_ID:
        return portal.translate(
            u'forwarding_task_type',
            domain='opengever.inbox',
            default=u'Forwarding'
        )

    voc = getTaskTypeVocabulary(portal)
    try:
        term = voc.getTerm(value)
    except LookupError:
        return value
    else:
        return term.title
