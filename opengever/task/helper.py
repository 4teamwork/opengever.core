from opengever.task import _
from opengever.task.util import getTaskTypeVocabulary
from plone.memoize import ram
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from opengever.base.browser.helper import css_class_from_obj, css_class_from_brain

@ram.cache(lambda m,i,value: value)
def task_type_helper(item, value):
    """Translate the task type with the vdex vocabulary, which provides
    its own translations stored in the vdex files.
    """
    if value == 'forwarding_task_type':
        return _(u'forwarding_task_type', default=u'Forwarding')

    voc = getTaskTypeVocabulary(getSite())
    try:
        term = voc.getTerm(value)
    except LookupError:
        return value
    else:
        return term.title

def linked(item, value):
    if not isinstance(value, unicode):
        value = value.decode('utf-8')
    url_method = lambda: '#'
    #item = hasattr(item, 'aq_explicit') and item.aq_explicit or item
    if hasattr(item, 'getURL'):
        url_method = item.getURL
    elif hasattr(item, 'absolute_url'):
        url_method = item.absolute_url
    css = ''
    if hasattr(item, 'getObject'):
        css = css_class_from_brain(item)
    else:
        css = css_class_from_obj(item)
    breadcrumb_titles = []
    breadcrumbs_view = getMultiAdapter((item, item.REQUEST),
                                       name='breadcrumbs_view')

    for elem in breadcrumbs_view.breadcrumbs():
        if isinstance(elem.get('Title'), unicode):
            breadcrumb_titles.append(elem.get('Title'))
        else:
            breadcrumb_titles.append(elem.get('Title').decode('utf-8'))
    link = '<a class="rollover-breadcrumb" href="%s" title="%s">%s</a>' % (
        url_method(),
        " &gt; ".join(t for t in breadcrumb_titles),
            value)
    wrapper = '<span class="linkWrapper %s">%s</span>' % (css, link)
    return wrapper

def path_checkbox(item, value):
    try:
        return '<input type="checkbox" class="noborder selectable" name="paths:list" id="%s" value="%s" alt="Select %s" title="Select %s" />' % (item.id, item.getPath(),  item.Title, item.Title)
    except AttributeError:
        return '<input type="checkbox" class="noborder selectable" name="paths:list" id="%s" value="%s" alt="Select %s" title="Select %s" />' % (item.id, '/'.join(item.getPhysicalPath()),  item.Title(), item.Title())
