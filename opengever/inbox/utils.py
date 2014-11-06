from plone import api


def get_current_inbox(context):
    portal = api.portal.get()

    inbox_container = portal.listFolderContents(
        contentFilter={'portal_type': 'opengever.inbox.container'})

    if inbox_container:
        return inbox_container[0].get_current_inbox()

    return portal.listFolderContents(
        contentFilter={'portal_type': 'opengever.inbox.inbox'})[0]
