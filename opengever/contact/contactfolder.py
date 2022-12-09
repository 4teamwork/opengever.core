from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.contact.interfaces import IContactFolder
from opengever.ogds.base.wrapper import TeamWrapper
from opengever.ogds.models.team import Team
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

        if id_.startswith('team-'):
            team_id = int(id_.split('-')[-1])
            team = Team.query.get(team_id)
            if team:
                return TeamWrapper.wrap(self, team)

        if default is _marker:
            raise KeyError(id_)
        return default
