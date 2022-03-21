from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from plone import api
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(ITransitionExtender)
@adapter(ITaskTemplateFolderSchema, IBrowserRequest)
class TaskTemplateFolderTransitionExtender(TransitionExtender):

    def after_transition_hook(self, transition, disable_sync, transition_params):
        """Also execute transition (activate or inactivate) for nested
        TaskTemplateFolders.
        """
        wftool = api.portal.get_tool("portal_workflow")
        catalog = api.portal.get_tool("portal_catalog")
        query = {'path': {'query': '/'.join(self.context.getPhysicalPath()),
                          'depth': 1},
                 'object_provides': ITaskTemplateFolderSchema.__identifier__,
                 'exclude_root': True}
        brains = catalog.unrestrictedSearchResults(query)
        for brain in brains:
            sub_tasktemplatefolder = brain.getObject()
            wftool.doActionFor(sub_tasktemplatefolder,
                               transition,
                               disable_sync=disable_sync,
                               transition_params=transition_params)
