from opengever.base.monkey.patching import MonkeyPatch
from zope.component import getAdapter


class PatchWorkflowTool(MonkeyPatch):

    def __call__(self):

        def doActionFor(self, ob, action, wf_id=None, *args, **kw):
            from opengever.base.transition import ITransitionExtender
            adapter = getAdapter(ob, ITransitionExtender, name=action)
            values = adapter.deserialize(**kw)
            value = original_doActionFor(self, ob, action, wf_id=wf_id, *args, **kw)

            adapter.after_transition_hook(transition=action, **values)

            return value

        from Products.CMFPlone.WorkflowTool import WorkflowTool
        locals()['__patch_refs__'] = False
        original_doActionFor = WorkflowTool.doActionFor

        self.patch_refs(WorkflowTool, 'doActionFor', doActionFor)
