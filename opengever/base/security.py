from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.queue import getQueue
from contextlib import contextmanager
from opengever.base.interfaces import IInternalWorkflowTransition
from plone import api
from Products.CMFCore.CMFCatalogAware import CatalogAware
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from opengever.ogds.base.sources import is_solr_feature_enabled


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
