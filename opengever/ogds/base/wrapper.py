from opengever.base.wrapper import SQLWrapperBase
from opengever.contact.utils import get_contactfolder_url
from opengever.ogds.base.interfaces import ITeam
from zope.interface import implements


class TeamWrapper(SQLWrapperBase):
    """Wrapper object for Teams (only stored in the OGDS database).
    """

    implements(ITeam)

    def absolute_url(self):
        return '{}/team-{}/view'.format(
            get_contactfolder_url(), self.model.team_id)

    def get_title(self):
        return self.model.label()
