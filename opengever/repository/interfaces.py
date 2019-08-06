from zope import schema
from zope.interface import Interface

DEFAULT_REPOSITORY_DEPTH = 3


class IRepositoryFolder(Interface):
    """Marker Interface for content type Repository Folder
    """


class IRepositoryFolderRecords(Interface):
    """ Configuration for repository folder
    """

    maximum_repository_depth = schema.Int(title=u'Maximum Repository Depth',
                                          default=DEFAULT_REPOSITORY_DEPTH)

    show_documents_tab = schema.Bool(title=u'Show documents tab on repository folder',
                                     default=True)

    show_tasks_tab = schema.Bool(title=u'Show tasks tab on repository folder',
                                 default=True)

    show_proposals_tab = schema.Bool(
        title=u'Show proposals tab on repository folder',
        default=True)


class IDuringRepositoryDeletion(Interface):
    """Request layer to indicate that repository is being deleted
    using the RepositoryDeleter.
    """
