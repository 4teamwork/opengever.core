from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from contextlib import contextmanager
from opengever.base.interfaces import IInternalWorkflowTransition
from plone import api
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


@contextmanager
def elevated_privileges():
    """Temporarily elevate current user's privileges.

    See http://docs.plone.org/develop/plone/security/permissions.html#bypassing-permission-checks
    for more documentation on this code.

    """
    old_manager = getSecurityManager()
    try:
        # Clone the current user and assign a new role.
        # Note that the username (getId()) is left in exception
        # tracebacks in the error_log,
        # so it is an important thing to store.
        tmp_user = UnrestrictedUser(
            api.user.get_current().getId(), '', ('manage', 'Manager'), ''
            )

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
