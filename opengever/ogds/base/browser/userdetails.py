from opengever.contact.utils import get_contactfolder_url
from opengever.ogds.base.utils import groupmembers_url
from opengever.ogds.models.service import ogds_service
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class UserDetails(BrowserView):
    """Displays infos about a user.
    """

    @classmethod
    def url_for(cls, userid):
        portal = getSite()
        return '/'.join((portal.portal_url(), '@@user-details',
                         userid))

    def user_details_table(self):
        template = ViewPageTemplateFile('templates/userdetails_table.pt')
        return template(self, self.request)

    def get_userdata(self):
        """Returns a dict of information about a specific user
        """
        user = ogds_service().fetch_user(
            self.userid, username_as_fallback=True)

        if not user:
            raise NotFound

        teams = []
        for group in user.groups:
            teams += group.teams

        return {'user': user, 'groups': user.groups, 'teams': teams}

    def publishTraverse(self, request, name):  # noqa
        """The name is the userid of the user who should be displayed.
        """
        self.userid = name
        return self

    def contactfolder_url(team_id):
        return get_contactfolder_url() or ''

    def groupmembers_url(self, groupid):
        return groupmembers_url(groupid)
