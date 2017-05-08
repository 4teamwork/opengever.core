from opengever.base.portlets import add_navigation_portlet_assignment
from opengever.base.portlets import block_context_portlet_inheritance
from plone import api


def configure_inboxcontainer_portlets(container, event):
    """Block portlet inheritance.
    """

    block_context_portlet_inheritance(container)


def configure_inbox_portlets(inbox, event):
    """Block portlet inheritance and add navigation portlet.
    """
    block_context_portlet_inheritance(inbox)

    url_tool = api.portal.get_tool('portal_url')
    add_navigation_portlet_assignment(
        inbox,
        root=u'/'.join(url_tool.getRelativeContentPath(inbox)),
        topLevel=0)
