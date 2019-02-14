from opengever.base.monkey.patching import MonkeyPatch
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest


class PatchWorkflowTool(MonkeyPatch):

    def __call__(self):

        def doActionFor(self, ob, action, wf_id=None, disable_sync=False, transition_params=None, *args, **kw):
            from opengever.base.transition import ITransitionExtender

            adapter = queryMultiAdapter((ob, getRequest()), ITransitionExtender, name=action)
            if not adapter:
                return original_doActionFor(self, ob, action, wf_id=wf_id, *args, **kw)

            if not transition_params:
                transition_params = {}

            values = adapter.deserialize(transition_params=transition_params)

            original_doActionFor(self, ob, action, wf_id=wf_id, *args, **kw)
            return adapter.after_transition_hook(
                transition=action, disable_sync=disable_sync,
                transition_params=values)

        from Products.CMFPlone.WorkflowTool import WorkflowTool
        locals()['__patch_refs__'] = False
        original_doActionFor = WorkflowTool.doActionFor

        self.patch_refs(WorkflowTool, 'doActionFor', doActionFor)
