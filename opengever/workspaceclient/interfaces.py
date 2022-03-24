from zope import schema
from zope.interface import Attribute
from zope.interface import Interface


class IWorkspaceClientSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable workspace client feature',
        description=u'Whether a remote workspace integration is enabled',
        default=False)

    is_linking_enabled = schema.Bool(
        title=u'Enable linking',
        description=u'Whether existing workspaces can be linked to a dossier.',
        default=True)


class ILinkedWorkspaces(Interface):
    """Behavior interface to manage remote workspaces
    """


class ILinkedDocuments(Interface):
    """Manages document links between GEVER document and their copies in TR.

    A GEVER document may be copied to one or more workspaces. This adapter
    manages links between these documents by referencing the other(s) via
    their UID.
    """

    linked_workspace_documents = Attribute("List of linked workspace docs")
    linked_gever_document = Attribute("Linked GEVER document")

    def link_workspace_document(workspace_doc_uid):
        """Add a link to a workspace document (by UID) to a GEVER doc.
        """

    def link_gever_document(gever_doc_uid):
        """Add a link to a GEVER document (by uid) to a workspace doc.
        """

    def serialize():
        """Serialize links as a JSON compatible data structure.
        """


class ILinkedToWorkspace(Interface):
    """Marker interface to mark dossiers with linked workspace
    """
