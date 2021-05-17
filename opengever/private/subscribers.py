from opengever.base.placeful_workflow import assign_placeful_workflow
from opengever.base.portlets import block_context_portlet_inheritance


def configure_private_root(root, event):
    block_context_portlet_inheritance(root)
    assign_placeful_workflow(root, "opengever_private_policy")
