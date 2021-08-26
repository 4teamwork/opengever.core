from opengever.base.security import elevated_privileges
from opengever.base.utils import check_group_plugin_configuration
from opengever.ogds.models.group import Group
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.interface import alsoProvides


class ReactivateLocalGroupPost(Service):

    def check_preconditions(self, groupname):
        check_group_plugin_configuration(self.context)

        if not groupname:
            raise BadRequest("Property 'groupname' is required.")

        self.ogds_group = Group.query.get(groupname)
        if not self.ogds_group:
            raise BadRequest('Group {} does not exist in OGDS.'.format(groupname))

        if self.ogds_group.active:
            raise BadRequest('Can only reactivate inactive groups.')
        if not self.ogds_group.is_local:
            raise BadRequest('Can only reactivate local groups.')

    def reply(self):
        data = json_body(self.request)

        groupname = data.get("groupname", None)
        self.check_preconditions(groupname)

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        gtool = getToolByName(self.context, "portal_groups")
        success = gtool.addGroup(groupname)
        if not success:
            raise BadRequest("Error occurred, could not add group {}.".format(groupname))

        # Add members
        group = gtool.getGroupById(groupname)
        for user in self.ogds_group.users:
            with elevated_privileges():
                group.addMember(user.userid)

        self.ogds_group.active = True
        return self.reply_no_content()
