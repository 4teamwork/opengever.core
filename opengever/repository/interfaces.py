from zope import schema
from zope.interface import Interface


class IRepositoryFolder(Interface):
    """Marker Interface for content type Repository Folder
    """


class IRepositoryFolderRecords(Interface):
    """ Configuration for repository folder
    """

    maximum_repository_depth = schema.Int(title=u'Maximum Repository Depth',
                                          default=3)
