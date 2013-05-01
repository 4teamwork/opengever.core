from zope.component import getUtility

from plone.app.layout.viewlets import content
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry

from opengever.base.interfaces import ISequenceNumber, IBaseClientID
from opengever.ogds.base.interfaces import IContactInformation
from opengever.task.task import ITask
from opengever.base.browser.helper import get_css_class


class TaskByline(content.DocumentBylineViewlet):

    update = content.DocumentBylineViewlet.update

    def get_css_class(self):
        return get_css_class(self.context)

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
