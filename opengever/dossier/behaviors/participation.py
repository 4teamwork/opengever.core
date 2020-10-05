from opengever.base.vocabulary import wrap_vocabulary
from opengever.dossier import _
from opengever.dossier import events
from opengever.ogds.base.sources import UsersContactsInboxesSourceBinder
from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone.supermodel import model
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.interface import implements
from zope.interface import Interface


_marker = object()
PARTICIPANT_ADDED = 'Participant added'
PARTICIPANT_REMOVED = 'Participant removed'


# ------ behavior ------

class IParticipationAware(Interface):
    """ Participation behavior interface. Types using this behaviors
    are able to have participations.
    """


class IParticipationAwareMarker(Interface):
    """ Marker interface for IParticipationAware behavior
    """


class PloneParticipationHandler(object):
    """ IParticipationAware behavior / adpter factory
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


# -------- model --------

class IParticipation(model.Schema):
    """ Participation Form schema
    """

    contact = schema.Choice(
        title=_(u'label_contact', default=u'Contact'),
        description=_(u'help_contact', default=u''),
        source=UsersContactsInboxesSourceBinder(),
        required=True,
        )

    roles = schema.List(
        title=_(u'label_roles', default=u'Roles'),
        value_type=schema.Choice(
            source=wrap_vocabulary(
                'opengever.dossier.participation_roles',
                visible_terms_from_registry='opengever.dossier'
                '.interfaces.IDossierParticipants.roles'),
            ),
        required=True,
        missing_value=[],
        default=[],
        )

# --------- model class --------


class Participation(Persistent):
    """ A participation represents a relation between a contact and
    a dossier. The choosen contact can have one or more roles in this
    dossier.
    """
    implements(IParticipation)

    def __init__(self, contact, roles=[]):
        self.contact = contact
        self.roles = roles

    @property
    def roles(self):
        return self._roles

    @roles.setter
    def roles(self, value):
        if value is None:
            pass
        elif not isinstance(value, PersistentList):
            value = PersistentList(value)
        self._roles = value

    @property
    def role_list(self):
        return ', '.join(self.roles)

    def has_key(self, key):
        return hasattr(self, key)
