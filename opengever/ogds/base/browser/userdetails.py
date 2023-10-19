from opengever.contact.utils import get_contactfolder_url
from opengever.ogds.base.mappings import username_to_userid
from opengever.ogds.base.utils import groupmembers_url
from opengever.ogds.models.exceptions import RecordNotFound
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
    def url_for(cls, username):
        portal = getSite()
        return '/'.join((portal.portal_url(), '@@user-details',
                         username))

    def user_details_table(self):
        template = ViewPageTemplateFile('templates/userdetails_table.pt')
        return template(self, self.request)

    def get_userdata(self):
        """Returns a dict of information about a specific user
        """
        try:
            user = ogds_service().find_user(username_to_userid(self.username))
        except RecordNotFound:
            raise NotFound

        teams = []
        for group in user.groups:
            teams += group.teams

        return {'user': user, 'groups': user.groups, 'teams': teams}

    def publishTraverse(self, request, name):  # noqa
        """The name is the userid of the user who should be displayed.
        """
        self.username = name
        return self

    def contactfolder_url(team_id):
        return get_contactfolder_url() or ''

    def groupmembers_url(self, groupid):
        return groupmembers_url(groupid)
