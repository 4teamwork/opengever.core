from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.private')

MEMBERSFOLDER_ID = 'private'


def enable_opengever_private():
    mtool = api.portal.get_tool('portal_membership')
    if not mtool.getMemberareaCreationFlag():
        mtool.setMemberareaCreationFlag()


def get_private_folder():
    membership_tool = api.portal.get_tool('portal_membership')
    home_folder = membership_tool.getHomeFolder()
    return home_folder


def get_private_folder_url():
    home_folder = get_private_folder()
    if not home_folder:
        return None
    return home_folder.absolute_url()
