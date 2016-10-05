from plone import api
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('opengever.private')

MEMBERSFOLDER_ID = 'private'


def enable_opengever_private():
    mtool = api.portal.get_tool('portal_membership')
    if not mtool.getMemberareaCreationFlag():
        mtool.setMemberareaCreationFlag()
