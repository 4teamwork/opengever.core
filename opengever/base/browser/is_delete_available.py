from Acquisition import aq_parent
from opengever.private.interfaces import IPrivateContainer
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from Products.Five.browser import BrowserView


class IsDeleteAvailable(BrowserView):
    """This view is used to check whether to display the delete
    button for a given object or not. This is notably usefull
    as we have our own delete actions for certain portal types.
    """

    authorized_interfaces = (IPrivateContainer,
                             ITaskTemplate,
                             ITaskTemplateFolderSchema)

    authorized_parent_interfaces = (IPrivateContainer,
                                    )

    def __call__(self):
        parent = aq_parent(self.context)
        return (any(interface.providedBy(self.context)
                for interface in self.authorized_interfaces)
                or any(interface.providedBy(parent)
                for interface in self.authorized_parent_interfaces)
                )
