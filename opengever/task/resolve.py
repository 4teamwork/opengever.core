from five import grok
from opengever.task.task import ITask


TASK_CLOSED_STATES = ['task-state-tested-and-closed',
                      'task-state-rejected',
                      'task-state-cancelled']


class ResolveCheck(grok.View):
    """This view checks if the task can be resolved.
    It will be called from a transition-expression """

    grok.context(ITask)
    grok.name('resolve_check')
    grok.require('zope2.View')

    def render(self):
        """check if there aren't any subtasks which aren't closed yet """

        wft = self.context.portal_workflow
        wf = wft.get(wft.getChainFor(self.context)[0])
        states = [s for s in wf.states]

        for state in TASK_CLOSED_STATES:
            states.pop(states.index(state))

        query = {
            'path' : {
                'query' : '/'.join(self.context.getPhysicalPath()),
                'depth' : -1},
            'portal_type': 'opengever.task.task',
            'review_state': states}

        if len(self.context.portal_catalog(query)) > 1:
            return False
        else:
            return True
