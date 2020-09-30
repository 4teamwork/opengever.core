from opengever.base.vocabulary import wrap_vocabulary
from opengever.dossier import _
from opengever.dossier import events
from opengever.ogds.base.sources import UsersContactsInboxesSourceBinder
from persistent import Persistent
from persistent.list import PersistentList
from plone.supermodel import model
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.interface import Interface, implements


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


class ParticipationHandler(object):
    """ IParticipationAware behavior / adpter factory
    """
    implements(IParticipationAware)
    annotation_key = 'participations'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def create_participation(self, *args, **kwargs):
        p = Participation(*args, **kwargs)
        return p

    def get_participations(self):
        return self.annotations.get(self.annotation_key,
                                    PersistentList())

    def get_participation_by_contact_id(self, contact_id):
        participations = list(self.get_participations())
        for participation in participations:
            if participation.contact == contact_id:
                return participation

    def update_participation(self, value, roles):
        value.roles = roles
        notify(events.ParticipationModified(self.context, value))

    def set_participations(self, value):
        if not isinstance(value, PersistentList):
            raise TypeError('Excpected PersistentList instance')
        self.annotations[self.annotation_key] = value

    def append_participiation(self, value):
        if not IParticipation.providedBy(value):
            raise TypeError('Excpected IParticipation object')
        if not self.has_participation(value):
            lst = self.get_participations()
            lst.append(value)
            self.set_participations(lst)
            notify(events.ParticipationCreated(self.context, value))

    def has_participation(self, value):
        return value in self.get_participations()

    def remove_participation(self, value, quiet=True):
        if not quiet and not self.has_participation(value):
            raise ValueError('Participation not in list')
        lst = self.get_participations()
        lst.remove(value)
        self.set_participations(lst)
        notify(events.ParticipationRemoved(self.context, value))
        del value


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
