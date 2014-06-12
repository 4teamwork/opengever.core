from five import grok
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.exceptions import RecordNotFound
from zExceptions import NotFound
from zope.app.component.hooks import getSite
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse


class UserDetails(grok.View):
    """Displays infos about a user.
    """

    grok.name('user-details')
    grok.context(Interface)
    grok.require('zope2.View')
    grok.implements(IPublishTraverse)

    @classmethod
    def url_for(self, userid):
        portal = getSite()
        return '/'.join((portal.portal_url(), '@@user-details',
                         userid))

    def get_userdata(self):
        """Returns a dict of information about a specific user
        """
        try:
            user = ogds_service().find_user(self.userid)
        except RecordNotFound:
            raise NotFound

        return {'user': user,
                'groups': user.groups}

    def publishTraverse(self, request, name):
        """The name is the userid of the user who should be displayed.
        """
        self.userid = name
        return self
