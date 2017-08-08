from five import grok
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.contact.interfaces import IContactFolder
from opengever.contact.models import Contact
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

        if default is _marker:
            raise KeyError(id_)
        return default


class ContactFolderAddForm(TranslatedTitleAddForm):
    grok.name('opengever.contact.contactfolder')


class ContactFolderEditForm(TranslatedTitleEditForm):
    grok.context(IContactFolder)
