from zope.component import getUtility

from plone.app.layout.viewlets import content
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry

from opengever.base.interfaces import ISequenceNumber, IBaseClientID
from opengever.octopus.tentacle.interfaces import IContactInformation
from opengever.task.task import ITask


class TaskByline(content.DocumentBylineViewlet):

    update = content.DocumentBylineViewlet.update

    @memoize
    def workflow_state(self):
        state = self.context_state.workflow_state()
        workflows = self.context.portal_workflow.getWorkflowsFor(
            self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state
    @memoize
    def sequence_number(self):
        seqNumb = getUtility(ISequenceNumber)
        return seqNumb.get_number(self.context)

    def responsible_link(self):
        info = getUtility(IContactInformation)
        task = ITask(self.context)
        return info.render_link(task.responsible)

    def client_id(self):
        # filing_client
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        return getattr(proxy, 'client_id')
