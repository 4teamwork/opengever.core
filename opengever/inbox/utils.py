from plone import api


def get_current_inbox(context):
    portal = api.portal.get()
    root_inbox = portal.listFolderContents(
        contentFilter={'portal_type': 'opengever.inbox.inbox'})[0]

    return root_inbox.get_current_inbox()
