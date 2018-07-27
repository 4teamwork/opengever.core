from contextlib import contextmanager
from opengever.sharing.interfaces import IDisabledPermissionCheck
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


@contextmanager
def disabled_permission_check():
    """This contextmanager allows to temporarily mark as a request
    with disabled permission checks, when fetching the sharing roles.
    """
    try:
        alsoProvides(getRequest(), IDisabledPermissionCheck)
        yield
    finally:
        noLongerProvides(getRequest(), IDisabledPermissionCheck)
