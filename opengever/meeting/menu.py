from opengever.base.menu import FilteredPostFactoryMenu
from opengever.meeting.committee import ICommittee
from zope.component import adapter
from zope.interface import Interface


@adapter(ICommittee, Interface)
class CommitteePostFactoryMenu(FilteredPostFactoryMenu):

    def is_filtered(self, factory):
        """Always filter out submitted proposal types, they can only be added
        by the system, never manually.

        """
        factory_id = factory.get('id')
        if factory_id == u'opengever.meeting.submittedproposal':
            return True

        return False
