from opengever.contact.utils import get_contactfolder_url
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.exceptions import RecordNotFound
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib import urlencode
from zExceptions import NotFound
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


class UserDetails(BrowserView):
    """Displays infos about a user.
    """

    @classmethod
    def url_for(cls, userid):
        return '{}/user-{}/view'.format(
            get_contactfolder_url(unrestricted=True), userid)

    def user_details_table(self):
        template = ViewPageTemplateFile('templates/userdetails_table.pt')
        return template(self, self.request)

    def get_user(self):
        try:
            return ogds_service().find_user(self.context.model.userid)
        except RecordNotFound:
            raise NotFound

    def get_userdata(self):
        """Returns a dict of information about a specific user
        """
        user = self.get_user()

        teams = []
        for group in user.groups:
            teams += group.teams

        return {'user': user, 'groups': user.groups, 'teams': teams}

    def contactfolder_url(team_id):
        return get_contactfolder_url()

    def groupmembers_url(self, groupid):
        portal = getSite()
        qs = urlencode({'group': groupid})
        return '/'.join((portal.portal_url(), '@@list_groupmembers?%s' % qs))


@implementer(IPublishTraverse)
class UserDetailsPlain(UserDetails):
    """Displays infos about a user.
    """

    def get_user(self):
        try:
            return ogds_service().find_user(self.userid)
        except RecordNotFound:
            raise NotFound

    def publishTraverse(self, request, name):  # noqa
        """The name is the userid of the user who should be displayed.
        """
        self.userid = name
        return self
