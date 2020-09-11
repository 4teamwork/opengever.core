from opengever.base.model import create_session
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import plone.protect.interfaces


ASSIGNABLE_ROLES = ['workspace_guest', 'workspace_member', 'workspace_admin']


def raise_for_unassignable_roles(roles):
    if roles is None:
        return
    for role in roles:
        if role not in ASSIGNABLE_ROLES:
            raise BadRequest(
                'Role {} cannot be assigned. Permitted roles are: {}'
                ''.format(role, ", ".join(ASSIGNABLE_ROLES)))


def get_sql_user(userid):
    """Returns the OGDS user object identified by `userid`.
    """
    return User.query.filter_by(userid=userid).one_or_none()


class GeverGroupsPost(Service):
    """Copy of plone.restapi.services.groups.add.GroupsPost modified
    to also add the created group into the OGDS.
    """

    def check_preconditions(self, groupname, roles):
        if not groupname:
            raise BadRequest("Property 'groupname' is required")

        gtool = getToolByName(self.context, "portal_groups")
        regtool = getToolByName(self.context, "portal_registration")

        if not regtool.isMemberIdAllowed(groupname):
            raise BadRequest("The group name you entered is not valid.")

        already_exists = gtool.getGroupById(groupname)
        if already_exists:
            raise BadRequest("The group name you entered already exists.")

        if Group.query.filter(Group.groupid == groupname).count() != 0:
            raise BadRequest('Group {} already exists in OGDS.'.format(groupname))

        raise_for_unassignable_roles(roles)

    def reply(self):
        portal = getSite()
        data = json_body(self.request)

        groupname = data.get("groupname", None)
        email = data.get("email", None)
        title = data.get("title", None)
        description = data.get("description", None)
        roles = data.get("roles", None)
        groups = data.get("groups", None)
        users = data.get("users", [])

        properties = {"title": title, "description": description, "email": email}

        self.check_preconditions(groupname, roles)

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        gtool = getToolByName(self.context, "portal_groups")
        success = gtool.addGroup(
            groupname,
            roles,
            groups,
            properties=properties,
            title=title,
            description=description,
        )
        if not success:
            raise BadRequest(
                "Error occurred, could not add group {}.".format(groupname)
            )

        # Add members
        group = gtool.getGroupById(groupname)
        for userid in users:
            with elevated_privileges():
                group.addMember(userid)

        # Add group to ogds
        session = create_session()

        ogds_group = Group(groupname, is_local=True)
        for userid in users:
            user = get_sql_user(userid)
            if user is None:
                raise BadRequest(
                    "User {} not found in OGDS.".format(userid)
                    )
            ogds_group.users.append(user)
        session.add(ogds_group)

        self.request.response.setStatus(201)
        self.request.response.setHeader(
            "Location", portal.absolute_url() + "/@groups/" + groupname
        )
        serializer = queryMultiAdapter((group, self.request), ISerializeToJson)
        return serializer()


@implementer(IPublishTraverse)
class GeverGroupsPatch(Service):
    """Copy of plone.restapi.services.groups.update.GroupsPatch
    """

    def __init__(self, context, request):
        super(GeverGroupsPatch, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@groups as parameters
        self.params.append(name)
        return self

    @property
    def _get_group_id(self):
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (group id)")
        return self.params[0]

    def _get_group(self, group_id):
        portal = getSite()
        portal_groups = getToolByName(portal, "portal_groups")
        return portal_groups.getGroupById(group_id)

    def check_preconditions(self):
        if not self.group:
            raise BadRequest("Trying to update a non-existing group.")

    def reply(self):
        data = json_body(self.request)
        self.group = self._get_group(self._get_group_id)

        title = data.get("title", None)
        description = data.get("description", None)
        roles = data.get("roles", None)
        groups = data.get("groups", None)
        users = data.get("users", {})

        self.check_preconditions()

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        portal_groups = getToolByName(self.context, "portal_groups")

        portal_groups.editGroup(
            self._get_group_id,
            roles=roles,
            groups=groups,
            title=title,
            description=description,
        )

        properties = {}
        for id, property in self.group.propertyItems():
            if data.get(id, False):
                properties[id] = data[id]

        self.group.setGroupProperties(properties)

        # Add/remove members
        memberids = self.group.getGroupMemberIds()
        for userid, allow in users.items():
            if allow:
                if userid not in memberids:
                    self.group.addMember(userid)
            else:
                if userid in memberids:
                    self.group.removeMember(userid)

        return self.reply_no_content()
