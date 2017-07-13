from opengever.base.portlets import add_navigation_portlet_assignment
from opengever.base.portlets import block_context_portlet_inheritance
from plone import api


def configure_templatefolder_portlets(templatefolder, event):
    """Added Eventhandler which configure portlets:

     - Do not acquire portlets, when templatefolder is not a subtemplatefolder
     - Add navigation portlet assignments as context portlet
    """

    if templatefolder.is_subtemplatefolder():
        return

    block_context_portlet_inheritance(templatefolder)

    url_tool = api.portal.get_tool('portal_url')
    add_navigation_portlet_assignment(
        templatefolder,
        root=u'/'.join(url_tool.getRelativeContentPath(templatefolder)),
        topLevel=0)
