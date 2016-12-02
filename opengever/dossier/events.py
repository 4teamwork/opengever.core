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


class ParticipationRemoved(ObjectEvent):
    """The `ParticipationRemoved` is fired before a participation is removed.
    """

    implements(interfaces.IParticipationRemoved)

    def __init__(self, obj, participant):
        self.object = obj
        self.participant = participant


class SourceFileErased(ObjectEvent):
    """The `SourceFileErased` is fired after the source file of a document
    is erased during a maintenance job.
    """

    implements(interfaces.ISourceFileErased)
