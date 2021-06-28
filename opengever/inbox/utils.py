from Acquisition import aq_chain
from opengever.inbox.inbox import IInbox
from plone import api


def get_current_inbox(context):
    portal = api.portal.get()

    inbox_container = portal.listFolderContents(
        contentFilter={'portal_type': 'opengever.inbox.container'})

    if inbox_container:
        return inbox_container[0].get_current_inbox()

    inbox = portal.listFolderContents(
        contentFilter={'portal_type': 'opengever.inbox.inbox'})

    return inbox[0] if inbox else None


def is_within_inbox(context):
    """ Checks, if the content is within the inbox.
    """
    return bool(filter(IInbox.providedBy, aq_chain(context)))
