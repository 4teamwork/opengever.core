from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.queue import getQueue
from contextlib import contextmanager
from ftw.solr.interfaces import ISolrSearch
from opengever.base import is_solr_feature_enabled
from opengever.base.interfaces import IInternalWorkflowTransition
from opengever.ogds.models.service import ogds_service
from opengever.workspace import is_workspace_feature_enabled
from plone import api
from Products.CMFCore.CMFCatalogAware import CatalogAware
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """

    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


def reindex_object_security_without_children(obj):
    """Reindex only the security indices of the passed in object.

    Sometimes we know we do not need to also reindex the security of all the
    child objects, so we can directly go to what the upstream implementation
    does per object.

    As we're bypassing the normal machinery, likewise we need to do Solr
    indexing by hand.
    """
    catalog = api.portal.get_tool('portal_catalog')
    security_idxs = CatalogAware._cmf_security_indexes

    catalog.reindexObject(obj, idxs=security_idxs, update_metadata=False)

    if is_solr_feature_enabled():
        # Using catalogs reindexObject does not trigger corresponding solr
        # reindexing, so we do it manually.

        # Register collective.indexing hook, to make sure solr changes
        # are realy send to solr. See
        # collective.indexing.queue.IndexQueue.hook.
        getQueue().hook()

        processor = getUtility(IIndexQueueProcessor, name='ftw.solr')
        processor.index(obj, security_idxs)


@contextmanager
def elevated_privileges(user_id=None):
    """Temporarily elevate current user's privileges.

    If the `user_id` argument is set, it will be user as the ID of the
    temporary user with elevated_privileges, otherwise the current user's ID
    will be used.

    See http://docs.plone.org/develop/plone/security/permissions.html#bypassing-permission-checks
    for more documentation on this code.

    """
    old_manager = getSecurityManager()
    try:
        # Clone the current user and assign a new role.
        # Note that the username (getId()) is left in exception
        # tracebacks in the error_log,
        # so it is an important thing to store.
        if user_id is None:
            user_id = api.user.get_current().getId()

        tmp_user = UnrestrictedUser(user_id, '', ('manage', 'Manager'), '')

        # Wrap the user in the acquisition context of the portal
        tmp_user = tmp_user.__of__(api.portal.get().acl_users)
        newSecurityManager(getRequest(), tmp_user)

        yield
    finally:
        # Restore the old security manager
        setSecurityManager(old_manager)


@contextmanager
def as_internal_workflow_transition():
    """This contextmanager allows to temporarily mark the request as an
    internal workflow transition request.

    Some transitions are only available when be triggered by code,
    for example the `planned to open` transition of tasks.
    """
    try:
        # mark request with marker interface
        alsoProvides(getRequest(), IInternalWorkflowTransition)

        yield
    finally:
        # remove marker interface
        noLongerProvides(getRequest(), IInternalWorkflowTransition)


class TeamraumSecurityHandler:
    """We need a special security handling for users and groups in teamraum.

    In general, every user can get information about every other user and group if he knows
    the id of that user/group. We also expose user listings, i.e. we list all members of a group
    or we list all groups a user is a member of.

    The teamraum is made for work with external users. An internal user can create differen worskapces for
    different external customers. The general approach of exposing users and groups to all users is now no longer
    satisfying. We need to restrict the visible users and groups to an external user to the once which are
    participating to the same workspaces.

    This object provides the functionality to do this checks in a performant way.
    """

    ACCESS_ALL_USERS_AND_GROUPS_PERMISSION = 'opengever.workspace: Access all users and groups'

    def is_teamraum(self):
        return is_workspace_feature_enabled()

    def has_all_users_and_groups_permission(self):
        return api.user.has_permission(self.ACCESS_ALL_USERS_AND_GROUPS_PERMISSION)

    def can_access_all_principals(self):
        if not self.is_teamraum():
            # The teamraum security is only activated if we're on a teamraum deployment
            return True

        return self.has_all_users_and_groups_permission()

    def can_access_principal(self, principal_id):
        if self.can_access_all_principals():
            return True

        return principal_id in self.get_whitelisted_principals()

    def get_whitelisted_principals(self):
        """This function returns a list of all principals which are
        whitelisted to access for the current user.

        Whitelisted principals are all user and group ids which are participating
        to the same workspaces as the current logged in user.
        """
        allowed_users_and_groups = []
        allowed_users_and_groups += self.extract_allowed_users_and_groups()
        allowed_users_and_groups += self.extract_group_members(allowed_users_and_groups)
        allowed_users_and_groups += [api.user.get_current().getId()]

        return set(allowed_users_and_groups)

    def extract_allowed_users_and_groups(self):
        catalog = api.portal.get_tool('portal_catalog')
        zcatalog = catalog._catalog

        workspace_brains = catalog(portal_type="opengever.workspace.workspace")
        allowedRolesAndUsers_index = zcatalog.getIndex('allowedRolesAndUsers')
        rids = [zcatalog.uids[brain.getPath()] for brain in workspace_brains]

        allowedRolesAndUsers_facet = set()
        [allowedRolesAndUsers_facet.update(allowedRolesAndUsers_index.getEntryForObject(rid)) for rid in rids]

        return [
            index_value.split('user:')[-1]
            for index_value in allowedRolesAndUsers_facet
            if index_value.startswith('user:')
        ]

    def extract_group_members(self, groupids):
        group_members = []
        for groupid in groupids:
            group = ogds_service().fetch_group(groupid)
            if not group:
                continue

            group_members += [user.userid for user in group.users]
        return group_members
