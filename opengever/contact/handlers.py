from opengever.base.portlets import block_context_portlet_inheritance


def configure_contactfolder_portlets(contactfolder, event):
    """Do not acquire portlets.
    """
    block_context_portlet_inheritance(contactfolder)
