from opengever.base.wrapper import SQLWrapperBase
from zope.interface import implements
from zope.interface import Interface


class IParticipationWrapper(Interface):
    """Marker interface for participation object wrappers."""


class ParticipationWrapper(SQLWrapperBase):

    implements(IParticipationWrapper)

    def absolute_url(self):
        return self.model.get_url(self.parent)
