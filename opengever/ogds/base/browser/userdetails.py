from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse


class UserDetails(grok.View):
    """Displays infos about a user.
    """

    grok.name('user-details')
    grok.context(Interface)
    grok.require('zope2.View')
    grok.implements(IPublishTraverse)

    def get_userdata(self):
        """Returns a dict of information about a specific user
        """
        info = getUtility(IContactInformation)
        user = info.get_user(self.userid)
        groups = info.list_user_groups(self.userid)

        return {'user': user,
                'userid': self.userid,
                'fullname': info.describe(self.userid),
                'groups': groups}

    def publishTraverse(self, request, name):
        """The name is the userid of the user who should be displayed.
        """
        self.userid = name
        return self
