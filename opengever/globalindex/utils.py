from Products.CMFPlone.utils import getToolByName
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from zope.app.component.hooks import getSite
from zope.component import queryUtility


def indexed_task_link(item, display_client=False):
    """Renders a indexed task item (globalindex sqlalchemy object) either
    with a link to the effective task (if the user has access) or just with
    the title.
    """

    # render icon image
    if item.icon:
        image = '<img src="%s" /> ' % item.icon
    else:
        image = ''

    # get the contact information utlity and the client
    info = queryUtility(IContactInformation)
    if info:
        client = info.get_client_by_id(item.client_id)
    if not info or not client:
        return '%s<span>%s</span>' % (image, item.title)

    # has the user access to the target task?
    has_access = False
    mtool = getToolByName(getSite(), 'portal_membership')
    member = mtool.getAuthenticatedMember()

    if member:
        principals = set(member.getGroups() + [member.getId()])
        allowed_principals = set(item.principals)
        has_access = len(principals & allowed_principals) > 0

    # is the target on a different client? we need to make a popup if
    # it is...
    if item.client_id != get_client_id():
        link_target = ' target="_blank"'
    else:
        link_target = ''

    # embed the client
    if display_client:
        client_html = ' <span class="discreet">(%s)</span>' % client.title
    else:
        client_html = ''

    # render the full link if he has acccess
    inner_html = ''.join((image, item.title, client_html))
    if has_access:
        return '<a href="%s"%s>%s</a>' % (
            client.public_url + '/' + item.physical_path,
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
