from opengever.private import MEMBERSFOLDER_ID
from plone import api


def configure_members_area(site):
    """Configure and enable Plone's MemberAreaCreation.
    """
    mtool = api.portal.get_tool('portal_membership')
    mtool.setMembersFolderById(MEMBERSFOLDER_ID)
    mtool.setMemberAreaType('opengever.private.folder')
