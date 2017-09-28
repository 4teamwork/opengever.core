from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import INoAutomaticInitialVersion
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class NoAutomaticInitialVersion(object):
    """Contextmanager that temporarily disables automatic creation of
    initial versions via event handler.

    This is sometimes necessary when a transmogrifier pipeline is involved,
    i.e. during setup or migration.
    """

    def __enter__(self):
        alsoProvides(getRequest(), INoAutomaticInitialVersion)

    def __exit__(self, exc_type, exc_val, exc_tb):
        noLongerProvides(getRequest(), INoAutomaticInitialVersion)


def create_initial_version(context):
    manager = getMultiAdapter((context, getRequest()), ICheckinCheckoutManager)
    manager.create_initial_version()
