from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from plone.dexterity.content import Container
from plone.directives import form
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from zope.interface import implements


class IPrivateRoot(form.Schema):
    """PrivateRoot marker interface.
    """


class PrivateRoot(Container, TranslatedTitleMixin):
    """A private root, the container for all the PrivateFolders.
    """

    _ordering = 'unordered'

    implements(IHideFromBreadcrumbs)

    Title = TranslatedTitleMixin.Title
