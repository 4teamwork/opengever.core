from opengever.dossier import events
from opengever.dossier.behaviors.participation import IParticipation
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import Participation
from opengever.kub import is_kub_feature_enabled
from opengever.kub.sources import KuBContactsSourceBinder
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.sources import UsersContactsInboxesSourceBinder
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.event import notify
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
from zope.schema.vocabulary import getVocabularyRegistry


class InvalidParticipantId(Exception):
    """No participant found for the given participant_id.
    """


class DupplicateParticipation(Exception):
    """A participation already exists for the given participant
    on the current context.
    """


class MissingParticipation(Exception):
    """No participation found for the given participant on the
    given context.
    """


class InvalidRole(Exception):
    """Given role does not exist.
    """


class ParticipationHandler(object):
    implements(IParticipationAware)

    def __init__(self, context):
        self.context = context
        if is_kub_feature_enabled():
            self.handler = KuBParticipationHandler(context)
        else:
            self.handler = PloneParticipationHandler(context)

    def __getattr__(self, name):
        return getattr(self.handler, name)


class ParticipationHandlerBase(object):
    """Base class for the PloneParticipationHandler and SQLParticipationHandler.
    """

    def validate_roles(context, roles):
        if not roles:
            raise InvalidRole("A list of roles is required")
        available_roles = getVocabularyRegistry().get(context, "opengever.dossier.participation_roles")
        for role in roles:
            if role not in available_roles:
                raise InvalidRole(u"Role '{}' does not exist".format(role))


class PloneParticipationHandler(ParticipationHandlerBase):
    """ IParticipationAware behavior / adapter factory.
    """
    annotation_key = 'participations'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)
        self.participant_source = UsersContactsInboxesSourceBinder()(self.context)

    def validate_participant(self, participant_id):
        try:
            self.participant_source.getTermByToken(participant_id)
        except LookupError:
            raise InvalidParticipantId(
                u"{} is not a valid id".format(participant_id))

    def add_participation(self, participant_id, roles, validate=True):
        if validate:
            self.validate_participant(participant_id)
            self.validate_roles(roles)
        if self.has_participation(participant_id):
            raise DupplicateParticipation(
                u"There is already a participation for {}".format(participant_id))
        participation = self.create_participation(participant_id, roles)
        self.append_participation(participation)
        self.context.reindexObject(idxs=["participations", "UID"])
        return participation

    def create_participation(self, participant_id, roles):
        return Participation(participant_id, roles)

    @property
    def _participations(self):
        return self.annotations.get(self.annotation_key)

    @_participations.setter
    def _participations(self, value):
        self.annotations[self.annotation_key] = value

    def get_participations(self):
        participations = self._participations or PersistentDict()
        return participations.values()

    def get_participation(self, participant_id):
        if not self._participations:
            return None
        return self._participations.get(participant_id)

    def update_participation(self, participant_id, roles):
        self.validate_participant(participant_id)
        self.validate_roles(roles)
        if not self.has_participation(participant_id):
            raise MissingParticipation(
                u"{} has no participations on this context".format(participant_id))
        self._participations[participant_id].roles = roles
        self.context.reindexObject(idxs=["participations", "UID"])
        notify(events.ParticipationModified(
            self.context, self._participations[participant_id]))

    def append_participation(self, value):
        if not IParticipation.providedBy(value):
            raise TypeError('Excpected IParticipation object')

        if self.has_participation(value.contact):
            raise DupplicateParticipation(
                u"There is already a participation for {}".format(value.contact))

        if self._participations is None:
            self._participations = PersistentDict()
        self._participations[value.contact] = value
        notify(events.ParticipationCreated(self.context, value))

    def has_participation(self, participant_id):
        return self._participations and participant_id in self._participations

    def remove_participation(self, participant_id):
        if not self.has_participation(participant_id):
            raise MissingParticipation(
                u"{} has no participations on this context".format(participant_id))
        participation = self._participations.pop(participant_id)
        self.context.reindexObject(idxs=["participations", "UID"])
        notify(events.ParticipationRemoved(self.context, participation))


class KuBParticipationHandler(PloneParticipationHandler):
    """ IParticipationAware behavior / adapter factory.
    """
    annotation_key = 'kub_participations'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)
        self.participant_source = KuBContactsSourceBinder(only_active=True)(self.context)


class IParticipationData(Interface):
    """Adapter interface to harmonize data accessors for
    plone and SQL participations.
    """

    def roles(self):
        """ Property returning the list of roles.
        """

    def participant_id(self):
        """ Property returning the participant_id.
        """

    def participant_title(self):
        """ Property returning the participant title.
        """


@implementer(IParticipationData)
@adapter(IParticipation)
class PloneOrKuBParticipationData(object):

    def __init__(self, participation):
        self._participation = participation

    @property
    def roles(self):
        # persistent list cannot be json serialized
        return list(self._participation.roles)

    @property
    def participant_id(self):
        return self._participation.contact

    @property
    def participant_title(self):
        actor = ActorLookup(self._participation.contact).lookup()
        return actor.get_label()
