from Acquisition import aq_parent
from opengever.dossier.templatedossier import ITemplateDossier
from opengever.dossier.templatefolder import ITemplateFolder
from opengever.meeting.interfaces import IParagraphTemplate
from opengever.private.interfaces import IPrivateContainer
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
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
    )

    authorized_parent_interfaces = (
        ITemplateDossier,
        ITemplateFolder,
        IPrivateContainer,
    )

    def __call__(self):
        parent = aq_parent(self.context)
        allowed = (
            # Whitelisted by interface provided by context
            any(interface.providedBy(self.context) for interface in self.authorized_interfaces),
            # Whitelisted by interface provided by the acquired parent
            any(interface.providedBy(parent) for interface in self.authorized_parent_interfaces),
        )
        return any(allowed)
