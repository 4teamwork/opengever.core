from five import grok
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.ogds.base.utils import get_current_org_unit
from plone.dexterity.content import Container
from plone.directives import form


class IInboxContainer(form.Schema):
    """Base schema for a the inbox container.
    """


class InboxContainerAddForm(TranslatedTitleAddForm):
    grok.name('opengever.inbox.container')


class InboxContainerEditForm(TranslatedTitleEditForm):
    grok.context(IInboxContainer)


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
