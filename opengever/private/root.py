from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from plone.dexterity.content import Container
from plone.supermodel import model
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from zope.interface import implements


class IPrivateRoot(model.Schema):
    """PrivateRoot marker interface.
    """


class PrivateRoot(Container, TranslatedTitleMixin):
    """A private root, the container for all the PrivateFolders.
    """

    implements(IHideFromBreadcrumbs)

    Title = TranslatedTitleMixin.Title

    location_prefix = 'P'
