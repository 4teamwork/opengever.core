from opengever.base.browser.helper import get_css_class
from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from Products.CMFPlone.utils import getToolByName
from zope.app.component.hooks import getSite
from zope.component import getUtility


def indexed_task_link(item, display_client=False):
    """Renders a indexed task item (globalindex sqlalchemy object) either
    with a link to the effective task (if the user has access) or just with
    the title.
    """

    site = getSite()

    css_class = get_css_class(item)
    service = ogds_service()

    # get the contact information utlity and the client
    admin_unit = service.fetch_admin_unit(item.admin_unit_id)
    if not admin_unit:
        return '<span class="%s">%s</span>' % (css_class, item.title)

    # has the user access to the target task?
    has_access = False
    mtool = getToolByName(site, 'portal_membership')
    member = mtool.getAuthenticatedMember()

    if member:
        principals = set(member.getGroups() + [member.getId()])
        allowed_principals = set(item.principals)

        # Administrators always have access, but the global role 'Administrator'
        # doesn't get indexed in task.principals in task indexer.
        # TODO: Avoid hardcoding 'og_administratoren'
        allowed_principals.add(u'og_administratoren')

        has_access = len(principals & allowed_principals) > 0

    # is the target on a different client? we need to make a popup if
    # it is...
    if item.admin_unit_id != get_current_admin_unit().id():
        link_target = ' target="_blank"'
        url = '%s/%s' % (admin_unit.public_url, item.physical_path)
    else:
        link_target = ''
        url = admin_unit.public_url + '/' + item.physical_path

    # embed the client
    if display_client:
        client_html = ' <span class="discreet">(%s)</span>' % admin_unit.title
    else:
        client_html = ''

    # create breadcrumbs including the (possibly remote) client title
    breadcrumb_titles = "[%s] > %s" % (admin_unit.title, item.breadcrumb_title)

    # render the full link if he has acccess
    inner_html = ''.join(('<span class="rollover-breadcrumb %s" \
                                 title="%s">%s</span>' % \
                    (css_class, breadcrumb_titles, item.title), client_html))
    if has_access:
        return '<a href="%s"%s>%s</a>' % (
            url,
            link_target,
            inner_html)
    else:
        return inner_html


def indexed_task_link_helper(item, value):
    """Tabbedview helper for rendering a link to a indexed task.
    The item has to be the Task sqlalchemy object.
    See `render_indexed_task` method.
    """

    return indexed_task_link(item)


def get_selected_items(context, request):
    """Returns a set of SQLAlchemy objects,
    equal if there is a "path:list" or a "task_id:list given in the request"
    """

    paths = request.get('paths', None)
    ids = request.get('task_ids', [])
    query = getUtility(ITaskQuery)

    if paths:
        relative_paths = []
        for path in paths:
            # cut the site id from the path
            relative_paths.append(
                '/'.join(path.split('/')[2:]))

        tasks = query.get_tasks_by_paths(relative_paths)
        keys = relative_paths
        attr = 'physical_path'

    elif ids:
        tasks = Task.query.by_ids(ids)
        keys = ids
        attr = 'task_id'

    else:
        # empty generator
        return

    # we need to sort the result by our ids list, because the
    # sql query result is not sorted...
    # create a mapping:
    mapping = {}
    for task in tasks:
        mapping[str(getattr(task, attr))] = task

    # get the task from the mapping
    for taskid in keys:
        task = mapping.get(str(taskid))
        if task:
            yield task
