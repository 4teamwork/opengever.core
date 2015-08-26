from five import grok
from opengever.base.menu import FilteredPostFactoryMenu
from opengever.meeting.committee import ICommittee
from opengever.repository.interfaces import IRepositoryFolder
from zope.interface import Interface


class CommitteePostFactoryMenu(FilteredPostFactoryMenu):
    grok.adapts(ICommittee, Interface)

    def is_filtered(self, factory):
        """Always filter out submitted proposal types, they can only be added
        by the system, never manually.

        """
        factory_id = factory.get('id')
        if factory_id == u'opengever.meeting.submittedproposal':
            return True

        return False


class RepositoryFolderPostFactoryMenu(FilteredPostFactoryMenu):
    grok.adapts(IRepositoryFolder, Interface)

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'opengever.meeting.meetingdossier':
            return True
