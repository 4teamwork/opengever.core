from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SecurityManagement import SpecialUsers
from contextlib import contextmanager
from zope.globalrequest import getRequest


@contextmanager
def changed_security(user=SpecialUsers.system):
    old_manager = getSecurityManager()
    newSecurityManager(getRequest(), user)

    yield

    setSecurityManager(old_manager)
