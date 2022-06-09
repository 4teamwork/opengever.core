from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import IParticipationAwareMarker
from zope.interface import classProvides
from zope.interface import implements
import logging


logger = logging.getLogger('opengever.setup.sections.set_dates')
PARTICIPATIONS_KEY = '_participations'


class ParticipationSection(object):
    """Transmogrifier section which adds dossier participations.
    """

    implements(ISection)
    classProvides(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')

    def __iter__(self):
        for item in self.previous:
            obj = self._get_obj(item)
            participations = item.get(PARTICIPATIONS_KEY, [])
            if participations:
                self.create_participations(obj, participations)
            yield item

    def create_participations(self, obj, participations):
        if not IParticipationAwareMarker.providedBy(obj):
            logger.warn(u'Participations for object {} ignored, participation '
                        'not supported for this type.'.format(obj))
            return

        handler = IParticipationAware(obj)

        for participation in participations:
            handler.add_participation(
                participation.get('participant_id'),
                participation.get('roles'),
                validate=False)

    def _get_obj(self, item):
        path = item.get(self.pathkey(*item.keys())[0], None)
        # Skip the Plone site object itself
        if not path:
            return None

        obj = self.context.unrestrictedTraverse(
            path.encode('utf-8').lstrip('/'), None)

        return obj
