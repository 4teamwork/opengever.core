from opengever.task import _
from opengever.task.util import getTaskTypeVocabulary
from plone.memoize import ram
from zope.app.component.hooks import getSite


@ram.cache(lambda m, i, value: value)
def task_type_helper(item, value):
    """Translate the task type with the vdex vocabulary, which provides
    its own translations stored in the vdex files.
    """
    portal = getSite()
    if value == 'forwarding_task_type':
        return portal.translate(
            _(u'forwarding_task_type', default=u'Forwarding'))

    voc = getTaskTypeVocabulary(portal)
    try:
        term = voc.getTerm(value)
    except LookupError:
        return value
    else:
        return term.title
