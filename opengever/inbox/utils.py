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
