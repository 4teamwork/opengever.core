from opengever.contact import is_contact_feature_enabled
from opengever.contact.models import Participation as SQLParticipation
from opengever.contact.sources import ContactsSource
from opengever.dossier import events
from opengever.dossier.behaviors.participation import IParticipation
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.behaviors.participation import Participation
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.event import notify
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


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


class ParticipationHandler(object):
    implements(IParticipationAware)

    def __init__(self, context):
        self.context = context
        if is_contact_feature_enabled():
            self.handler = SQLParticipationHandler(context)
        else:
            self.handler = PloneParticipationHandler(context)

    def __getattr__(self, name):
        return getattr(self.handler, name)


class PloneParticipationHandler(object):
    """ IParticipationAware behavior / adapter factory.
    """
    annotation_key = 'participations'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def add_participation(self, participant_id, roles):
        participation = self.create_participation(participant_id, roles)
        self.append_participation(participation)
        return participation

    def create_participation(self, participant_id, roles):
        p = Participation(participant_id, roles)
        return p

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
        return self._participations and self._participations.get(participant_id)

    def update_participation(self, participant_id, roles):
        if not self.has_participation(participant_id):
            raise ValueError("{} has no participations on this context".format(
                participant_id))
        self._participations[participant_id].roles = roles
        notify(events.ParticipationModified(
            self.context, self._participations[participant_id]))

    def append_participation(self, value):
        if not IParticipation.providedBy(value):
            raise TypeError('Excpected IParticipation object')

        if self.has_participation(value.contact):
            raise ValueError("There is already a participation for {}".format(
                value.contact))

        if self._participations is None:
            self._participations = PersistentDict()
        self._participations[value.contact] = value
        notify(events.ParticipationCreated(self.context, value))

    def has_participation(self, participant_id):
        return self._participations and participant_id in self._participations

    def remove_participation(self, participant_id, quiet=True):
        if not quiet and not self.has_participation(participant_id):
            raise ValueError('No participation for {}'.format(participant_id))
        participation = self._participations.pop(participant_id)
        notify(events.ParticipationRemoved(self.context, participation))


class SQLParticipationHandler(object):
    """ IParticipationAware behavior / adpter factory
    """

    def __init__(self, context):
        self.context = context

    def get_participations(self):
        query = SQLParticipation.query.by_dossier(self.context)
        for participation in query:
            yield participation

    def get_participation(self, participant_id):
        participant = self.get_participant(participant_id)
        query = participant.participation_class.query.by_participant(
            participant).by_dossier(self.context)
        participation = query.one_or_none()
        if not participation:
            raise MissingParticipation(
                "{} has no participations on this context".format(participant_id))
        return query.one_or_none()

    def has_participation(self, participant_id):
        try:
            self.get_participation(participant_id)
            return True
        except (MissingParticipation, InvalidParticipantId):
            return False

    def get_participant(self, participant_id):
        source = ContactsSource(self.context)
        try:
            term = source.getTermByToken(participant_id)
        except LookupError:
            raise InvalidParticipantId(
                "{} is not a valid id".format(participant_id))
        return term.value

    def add_participation(self, participant_id, roles):
        if self.has_participation(participant_id):
            raise DupplicateParticipation(
                "There is already a participation for {}".format(participant_id))

        participant = self.get_participant(participant_id)
        return participant.participation_class.create(
            participant=participant, dossier=self.context, roles=roles)

    def update_participation(self, participant_id, roles):
        participation = self.get_participation(participant_id)
        participation.update_roles(roles)

    def remove_participation(self, participant_id):
        participation = self.get_participation(participant_id)
        participation.delete()


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


@implementer(IParticipationData)
@adapter(IParticipation)
class PloneParticipationData(object):

    def __init__(self, participation):
        self._participation = participation

    @property
    def roles(self):
        return self._participation.roles

    @property
    def participant_id(self):
        return self._participation.contact


@implementer(IParticipationData)
@adapter(SQLParticipation)
class SQLParticipationData(object):

    def __init__(self, participation):
        self._participation = participation

    @property
    def roles(self):
        return [role.role for role in self._participation.roles]

    @property
    def participant_id(self):
        source = ContactsSource(self._participation.resolve_dossier())
        return source.getTerm(self._participation.participant).token
