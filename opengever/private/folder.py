from opengever.ogds.base.actor import Actor
from opengever.private import _
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from plone.app.content.interfaces import INameFromTitle
from plone.dexterity.content import Container
from zope import schema
from zope.component import adapts
from zope.interface import implements


class IPrivateFolder(IRepositoryFolderSchema, IPrivateContainer):
    """Private folder marker and schema interface.
    """

    userid = schema.TextLine(
        title=_(u'label_userid', default=u'User ID'),
        required=True,
    )


class PrivateFolder(Container):
    """A private folder, container for all PrivateDossiers.

    Created automatically by the portal_membership tool for every user on
    the first login.
    """

    def Title(self):
        return Actor.lookup(self.userid).get_label(self)


class PrivateFolderNameFromTitle(object):
    """An INameFromTitle adapter to make sure that the userid is used as id.
    """

    implements(INameFromTitle)
    adapts(IPrivateFolder)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return self.context.userid
