from five import grok
from opengever.base.model import create_session
from opengever.base.portlets import block_context_portlet_inheritance
from opengever.contact.models import Participation
from opengever.dossier.behaviors.dossier import IDossierMarker
from zope.lifecycleevent.interfaces import IObjectCopiedEvent


@grok.subscribe(IDossierMarker, IObjectCopiedEvent)
def copy_participations(copied_dossier, event):
    """Make sure that participations are copied as well when copying a dossier.
    """

    participations = Participation.query.by_dossier(event.original).all()
    if not participations:
        return

    session = create_session()
    for participation in participations:
        session.add(participation.copy_to_dossier(copied_dossier))


def configure_contactfolder_portlets(contactfolder, event):
    """Do not acquire portlets.
    """
    block_context_portlet_inheritance(contactfolder)
