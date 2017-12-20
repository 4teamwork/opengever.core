from opengever.base.sequence import DefaultSequenceNumberGenerator
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.workspace.interfaces import IWorkspace
from zope.component import adapter


@adapter(IDossierMarker)
class DossierSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """ All dossier-types should use the same range/key of sequence numbers.
    """

    @property
    def key(self):
        if IWorkspace.providedBy(self.context):
            # Workspaces provide the IWorkspace interface, but also
            # the IDossierMarker interface (behavior).
            # Registering the adapter for IWorkspace does not override the
            # IDossierMarker adapter, since they do not subclass each other.
            return 'WorkspaceSequenceNumberGenerator'
        return 'DossierSequenceNumberGenerator'
