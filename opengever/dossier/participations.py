from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import PloneParticipationHandler
from zope.interface import implements


class ParticipationHandler(object):
    implements(IParticipationAware)

    def __init__(self, context):
        self.context = context
        self.handler = PloneParticipationHandler(context)

    def __getattr__(self, name):
        return getattr(self.handler, name)
