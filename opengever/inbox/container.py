from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.ogds.base.utils import get_current_org_unit
from plone.dexterity.content import Container
from plone.supermodel import model


class IInboxContainer(model.Schema):
    """Base schema for a the inbox container.
    """


class InboxContainer(Container, TranslatedTitleMixin):
    """Inbox Container class, a container for all inboxes.
    This is used for installations with admin units containing
    multiple org_units. Because every org_unit has an inbox.
    """

    Title = TranslatedTitleMixin.Title

    def get_current_inbox(self):
        """Returns the subinbox of the current orgUnit if exists,
        otherwise None."""

        sub_inboxes = self.listFolderContents(
            contentFilter={'portal_type': 'opengever.inbox.inbox'})

        for inbox in sub_inboxes:
            if self.is_active_inbox(inbox):
                return inbox

        return None

    def is_active_inbox(self, inbox):
        return inbox.get_responsible_org_unit() == get_current_org_unit()
