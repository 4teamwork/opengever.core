from opengever.dossier.behaviors.dossier import IDossierMarker
from plone.app.textfield import RichText
from zope import schema
from zope.interface import Interface
from zope.schema import Datetime
from zope.schema import TextLine


class IWorkspaceRoot(Interface):
    """ Marker interface for Workspace Roots """


class IWorkspace(IDossierMarker):
    """ Marker interface for Workspace """


class IWorkspaceFolder(IDossierMarker):
    """ Marker interface for Workspace Folders """


class IWorkspaceSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable workspace feature',
        description=u'Whether workspace integration is enabled',
        default=False)


class IToDo(Interface):
    """ Marker interface for ToDos """


class IToDosContainer(Interface):
    """ Marker interface for ToDosContainers """


class IResponse(Interface):
    """Represents a response - Not a DX type"""

    text = RichText(required=True)
    created = Datetime(required=True)
    creator = TextLine(required=True)
    modified = Datetime(required=False)
    modifier = TextLine(required=False)


class IResponses(Interface):
    """Adapter for responses.
    """
