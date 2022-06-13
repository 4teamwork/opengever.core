from opengever.base.vocabulary import wrap_vocabulary
from opengever.dossier import _
from opengever.ogds.base.sources import UsersContactsInboxesSourceBinder
from persistent import Persistent
from persistent.list import PersistentList
from plone.supermodel import model
from zope import schema
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
