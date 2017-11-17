from AccessControl import getSecurityManager
from plone import api
import transaction


def create_members_folder(private_root):
    mtool = api.portal.get_tool('portal_membership')
    mtool.setMembersFolderById(private_root.id)
    mtool.setMemberAreaType('opengever.private.folder')

    mtool.createMemberArea()
    transaction.commit()

    return private_root.get(getSecurityManager().getUser().getId())
