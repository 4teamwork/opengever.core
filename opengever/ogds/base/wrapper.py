from opengever.base.wrapper import SQLWrapperBase
from opengever.contact.utils import get_contactfolder_url
from opengever.ogds.base.interfaces import ITeam
from opengever.ogds.base.interfaces import IUser
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


class UserWrapper(SQLWrapperBase):
    """Wrapper object for Users (only stored in the OGDS database).
    """

    implements(IUser)

    def absolute_url(self):
        return '{}/user-{}/view'.format(
            get_contactfolder_url(), self.model.userid)

    def get_title(self):
        return self.model.label()
