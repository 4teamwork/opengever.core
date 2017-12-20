from opengever.base.sequence import DefaultSequenceNumberGenerator
from opengever.workspace.interfaces import IWorkspace
from zope.component import adapter


@adapter(IWorkspace)
class WorkspaceSequenceNumberGenerator(DefaultSequenceNumberGenerator):
    """ All workspaces should use the same range/key of sequence numbers.
    """

    key = 'WorkspaceSequenceNumberGenerator'
