from opengever.dossier.behaviors.dossier import IDossierMarker
from plone.app.textfield import RichText
from zope import schema
from zope.interface import Attribute
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


class IAnnotationDataList(Interface):

    annotation_key = Attribute('Annotation key where the data ist stored.')
    writeable_attributes = Attribute('Tuple of writeable attribute names.')

    def __init__(context):
        """The data is stored in the annotations of the ``context``.
        """

    def all():
        """Return all items.
        """

    def get(item_id):
        """Get an item.
        """

    def create(**kwargs):
        """Create a new item.
        """

    def append(item):
        """Append an item.
        """

    def remove(item):
        """Remove an item.
        """


class IResponses(IAnnotationDataList):
    """Adapter for responses.
    """
