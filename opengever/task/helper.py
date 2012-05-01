from opengever.task import _
from opengever.task.util import getTaskTypeVocabulary
from plone.memoize import ram
from zope.app.component.hooks import getSite


@ram.cache(lambda m,i,value: value)
def task_type_helper(item, value):
    """Translate the task type with the vdex vocabulary, which provides
    its own translations stored in the vdex files.
    """
    portal = getSite()
    if value == 'forwarding_task_type':
        return portal.translate(_(u'forwarding_task_type', default=u'Forwarding'))

    voc = getTaskTypeVocabulary(portal)
    try:
        term = voc.getTerm(value)
    except LookupError:
        return value
    else:
        return term.title


def path_checkbox(item, value):
    try:
        path = item.getPath()
        title = item.Title
    except AttributeError:
        path = '/'.join(item.getPhysicalPath())
        title = item.Title()
    return '<input type="checkbox" class="noborder selectable" name="paths:list" id="%s" value="%s" alt="Select %s" title="Select %s" />' % (item.id, path, title, title)

