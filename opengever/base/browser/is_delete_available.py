from Acquisition import aq_chain
from Acquisition import aq_inner
from opengever.dossier.templatedossier import ITemplateDossier
from opengever.dossier.templatefolder import ITemplateFolder
from opengever.meeting.interfaces import IParagraphTemplate
from opengever.private.interfaces import IPrivateContainer
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceMeeting
from Products.Five.browser import BrowserView


class IsDeleteAvailable(BrowserView):
    """This view is used to check whether to display the delete
    button for a given object or not. This is notably usefull
    as we have our own delete actions for certain portal types.
    """

    authorized_interfaces = (
        IParagraphTemplate,
        IPrivateContainer,
        ITaskTemplate,
        ITaskTemplateFolderSchema,
        IWorkspaceMeeting,
    )

    authorized_parent_interfaces = (
        ITemplateDossier,
        ITemplateFolder,
        IPrivateContainer,
        IWorkspace,
    )

    def __call__(self):
        # Whitelisted by interface provided by context
        if any(interface.providedBy(self.context) for interface in self.authorized_interfaces):
            return True

        # Whitelisted by interface provided by one of its parents
        for obj in aq_chain(aq_inner(self.context)):
            if any(interface.providedBy(obj) for interface in self.authorized_parent_interfaces):
                return True

        return False
