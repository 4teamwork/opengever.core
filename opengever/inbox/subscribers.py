from opengever.base.placeful_workflow import assign_placeful_workflow
from opengever.base.portlets import add_navigation_portlet_assignment
from opengever.base.portlets import block_context_portlet_inheritance
from plone import api


def configure_inbox_container(container, event):
    block_context_portlet_inheritance(container)


def configure_inbox(inbox, event):
    block_context_portlet_inheritance(inbox)

    url_tool = api.portal.get_tool('portal_url')
    add_navigation_portlet_assignment(
        inbox,
        root=u'/'.join(url_tool.getRelativeContentPath(inbox)),
        topLevel=0)

    assign_placeful_workflow(inbox, "opengever_inbox_policy")
