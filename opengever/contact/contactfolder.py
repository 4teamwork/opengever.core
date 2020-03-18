from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.contact import is_contact_feature_enabled
from opengever.contact.interfaces import IContactFolder
from opengever.contact.models import Contact
from opengever.ogds.base.wrapper import TeamWrapper
from opengever.ogds.base.wrapper import UserWrapper
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from plone.dexterity.content import Container
from zope.interface import implements


_marker = object()


class ContactFolder(Container, TranslatedTitleMixin):
    """Container which contains all contacts.
    """

    implements(IContactFolder)

    Title = TranslatedTitleMixin.Title

    def _getOb(self, id_, default=_marker):
        """We extend `_getObj` in order to change the context for person
        objects to the `PersonWrapper`. That allows us to register the
        view for Persons as regular Browser view without any traversal hacks.
        """

        obj = super(ContactFolder, self)._getOb(id_, default)
        if obj is not default:
            return obj

        if id_.startswith('contact-'):
            contact_id = int(id_.split('-')[-1])
            contact = Contact.query.get(contact_id)
            if contact:
                return contact.get_wrapper(self)

        if id_.startswith('team-'):
            team_id = int(id_.split('-')[-1])
            team = Team.query.get(team_id)
            if team:
                return TeamWrapper.wrap(self, team)

        if id_.startswith('user-'):
            user_id = id_.split('-', 1)[-1]
            user = User.query.get(user_id)
            if user:
                return UserWrapper.wrap(self, user)

        if default is _marker:
            raise KeyError(id_)
        return default

    def allowedContentTypes(self, *args, **kwargs):
        types = super(ContactFolder, self).allowedContentTypes(*args, **kwargs)

        def filter_type(fti):
            if fti.id == "opengever.contact.contact":
                return not is_contact_feature_enabled()
            return True

        return filter(filter_type, types)
