from five import grok
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import INoAutomaticInitialVersion
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.lifecycleevent.interfaces import IObjectAddedEvent


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


@grok.subscribe(IDocumentSchema, IObjectAddedEvent)
def handle_document_added(context, event):
    """Event handler which creates a initial version when adding a new
    document. Since we use manual versioning for the document, the initial
    version doesn't get created automatically.

    """
    if INoAutomaticInitialVersion.providedBy(context.REQUEST):
        return

    create_initial_version(context)


def create_initial_version(context):
    # XXX remove this method
    return
