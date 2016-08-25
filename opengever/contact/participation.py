from opengever.base.wrapper import SQLWrapperBase
from zope.interface import implements
from zope.interface import Interface


class IParticipationWrapper(Interface):
    """Marker interface for participation object wrappers."""


class ParticipationWrapper(SQLWrapperBase):

    implements(IParticipationWrapper)
