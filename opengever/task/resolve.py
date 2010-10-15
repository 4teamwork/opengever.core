from five import grok
from opengever.task.task import ITask

RESOLVED_TASK_STATE = 'task-state-resolved'

class ResolveCheck(grok.CodeView):
    """The view wich check if the task can be resolved. 
    It would be called from the transition-expression """

    grok.context(ITask)
    grok.name('resolve_check')
    grok.require('zope2.View')

    def render(self):
        """check if there aren't any subtask wich aren't closed yet """

        wft = self.context.portal_workflow
        wf = wft.get(wft.getChainFor(self.context)[0])
        states = [s for s in wf.states]
        states.pop(states.index(RESOLVED_TASK_STATE))
        query = {
            'path' : {
                'query' : '/'.join(self.context.getPhysicalPath()),
                'depth' : -1,
            },
            'portal_type': 'opengever.task.task',
            'review_state': states,
        }
        if len(self.context.portal_catalog(query)) > 1:
            return False
        else:
            return True
