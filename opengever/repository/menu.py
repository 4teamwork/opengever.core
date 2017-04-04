from five import grok
from opengever.base.menu import FilteredPostFactoryMenu
from opengever.repository.interfaces import IRepositoryFolder
from zope.interface import Interface


class RepositoryFolderPostFactoryMenu(FilteredPostFactoryMenu):
    grok.adapts(IRepositoryFolder, Interface)

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'opengever.meeting.meetingdossier':
            return True
