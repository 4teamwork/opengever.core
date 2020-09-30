from opengever.dossier import interfaces
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class ParticipationCreated(ObjectEvent):
    """The `ParticipationCreated` is fired after a
    participation is created and added.
    """

    implements(interfaces.IParticipationCreated)

    def __init__(self, obj, participant):
        self.object = obj
        self.participant = participant


class ParticipationModified(ObjectEvent):
    """The `ParticipationModified` is fired after a
    participation is modified.
    """

    implements(interfaces.IParticipationModified)

    def __init__(self, obj, participant):
        self.object = obj
        self.participant = participant


class ParticipationRemoved(ObjectEvent):
    """The `ParticipationRemoved` is fired before a participation is removed.
    """

    implements(interfaces.IParticipationRemoved)

    def __init__(self, obj, participant):
        self.object = obj
        self.participant = participant


class DossierAttachedToEmailEvent(ObjectEvent):
    """The file was attached to an email by OfficeConnector."""

    implements(interfaces.IDossierAttachedToEmailEvent)

    def __init__(self, obj, documents=None):
        self.object = obj
        self.documents = documents
