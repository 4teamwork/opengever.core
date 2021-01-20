from Acquisition import aq_base
from logging import getLogger
from opengever.base.model import create_session
from opengever.ogds.models.group import Group
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

logger = getLogger('opengever.workspace.registration')


class SelfRegistrationView(BrowserView):
    """Handles self registration of users

       Creates the user in OGDS and redirects to the site root.
    """

    def __call__(self):
        if api.user.is_anonymous():
            return self.redirect_to_next()

        self.create_ogds_user()
        self.redirect_to_next()

    def redirect_to_next(self):
        next_url = self.request.form.get('next')
        portal_url = api.portal.get().absolute_url()
        if next_url:
            if next_url.startswith(portal_url):
                return self.request.response.redirect(next_url)
            elif next_url.startswith('/'):
                return self.request.response.redirect(portal_url + next_url)

        self.request.response.redirect(portal_url)

    def create_ogds_user(self):
        member = api.user.get_current()
        userid = member.getId()

        # Already exists?
        if ogds_service().fetch_user(userid):
            return

        # Only users in the current site
        acl_users = getToolByName(self, 'acl_users')
        user = aq_base(acl_users).getUserById(userid, None)
        if user is None:
            return

        session = create_session()
        firstname = member.getProperty('firstname', '')
        lastname = member.getProperty('lastname', '')
        email = member.getProperty('email')
        ogds_user = User(
            userid=userid,
            firstname=firstname,
            lastname=lastname,
            email=email)
        logger.info("Created OGDS entry for user %r" % userid)

        # Assign the intersection of existing OGDS groups and the newly created
        # user's groups as groups for the new OGDS user entry. This will most
        # likely be just the OrgUnit's users_group. If there's more, they
        # will be created and assigned during next sync.
        groups_of_new_user = member.getUser().getGroupIds()
        groups = Group.query.filter(Group.groupid.in_(groups_of_new_user)).all()
        ogds_user.groups = groups
        session.add(ogds_user)
