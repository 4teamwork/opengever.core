from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from opengever.tasktemplates.interfaces import IDuringTaskTemplateFolderWorkflowTransition
from plone import api
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(ITransitionExtender)
@adapter(ITaskTemplateFolderSchema, IBrowserRequest)
class TaskTemplateFolderTransitionExtender(TransitionExtender):

    def after_transition_hook(self, transition, disable_sync, transition_params):
        """Also execute transition (activate or inactivate) for nested
        TaskTemplateFolders.
        """
        # because this method is recursively called we need to add and remove
        # the IDuringTaskTemplateFolderWorkflowTransition only on the first
        # call the method
        added_interface = False
        if not IDuringTaskTemplateFolderWorkflowTransition.providedBy(self.request):
            alsoProvides(self.request, IDuringTaskTemplateFolderWorkflowTransition)
            added_interface = True

        wftool = api.portal.get_tool("portal_workflow")
        catalog = api.portal.get_tool("portal_catalog")
        query = {'path': {'query': '/'.join(self.context.getPhysicalPath()),
                          'depth': 1,
                          'exclude_root': True},
                 'object_provides': ITaskTemplateFolderSchema.__identifier__}
        brains = catalog.unrestrictedSearchResults(query)
        for brain in brains:
            sub_tasktemplatefolder = brain.getObject()
            wftool.doActionFor(sub_tasktemplatefolder,
                               transition,
                               disable_sync=disable_sync,
                               transition_params=transition_params)
        if added_interface:
            noLongerProvides(self.request, IDuringTaskTemplateFolderWorkflowTransition)
