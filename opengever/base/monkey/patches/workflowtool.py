from opengever.base.monkey.patching import MonkeyPatch
from zope.component import queryAdapter


class PatchWorkflowTool(MonkeyPatch):

    def __call__(self):

        def doActionFor(self, ob, action, wf_id=None, disable_sync=False, *args, **kw):
            from opengever.base.transition import ITransitionExtender

            adapter = queryAdapter(ob, ITransitionExtender, name=action)
            if not adapter:
                return original_doActionFor(self, ob, action, wf_id=wf_id, *args, **kw)

            values = adapter.deserialize(**kw)
            original_doActionFor(self, ob, action, wf_id=wf_id, *args, **kw)
            return adapter.after_transition_hook(
                transition=action, disable_sync=disable_sync, **values)

        from Products.CMFPlone.WorkflowTool import WorkflowTool
        locals()['__patch_refs__'] = False
        original_doActionFor = WorkflowTool.doActionFor

        self.patch_refs(WorkflowTool, 'doActionFor', doActionFor)
