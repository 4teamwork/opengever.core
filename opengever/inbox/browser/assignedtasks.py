"""Contains the view for Assigned Tasks"""
from opengever.inbox.browser.assignedforwardings import InboxAssignedForwardings
from five import grok
from opengever.inbox.inbox import IInbox


class InboxAssignedTasks(InboxAssignedForwardings):
    """Displays all Forwardings that are assigned to the Inbox
    """
    grok.name('tabbedview_view-assigned_tasks')
    grok.context(IInbox)

    displayStates = 'task-state-open'