from zope.component import getMultiAdapter
from zope.interface import Interface, implements
from Products.Five import BrowserView

TASK_CLOSED_STATES = ['task-state-tested-and-closed',
                      'task-state-rejected',
                      'task-state-cancelled']


class ITaskTransitionController(Interface):
    """Interface for a controller view for checking,
    if certain transitions should be available or not"""

    def is_re_open_possible():
        """Checks if:
        - The actual user is the issuer of the actual task(context)"""

    def is_progress_to_resolve_possible():
        """Checks if:
        - Task is not unidirectional_by_value (zu direkten Erledigung).
        - The responsible is the actual user.
        - All subtaskes are resolve, cancelled or closed.
        """

    def is_progress_to_closed_possible():
        """Checks if:
        - Task is unidirectional_by_value (zu direkten Erledigung).
        - All subtaskes are resolved, cancelled or closed.
        """

    def is_cancel_possible():
        """Checks if:
        - The actual user is the issuer."""

    def is_open_to_progress_possible():
        """Checks if ...
        - Not unidirectional_by_reference
        - The user is not the issuer, appart from he's also the responsible
        """

    def is_reject_possible():
        """Checks if ...
        - The actual user is the responsible.
        """

    def is_open_to_resolve_possible():
        """Checks if:
        - All subtaskes are resolved, cancelled or closed.
        - The Task is is_bidirectional
        - The user is not the issuer, appart from he's also the responsible
        """

    def is_open_to_close_possible():
        """Checks if:
        - The user is the issuer or is a unidirectional_byrefrence task"""

    def is_rejected_to_open_possible():
        """Checks if:
        - The actual user is the issuer of the task"""

    def is_resolve_to_open_possible():
        """Checks if:
        - The actual user is the issuer of the task"""

    def is_resolve_to_closed_possible():
        """Checks if:
        - The actual user is the issuer of the task"""


class TaskTransitionController(BrowserView):
    """Controller View: see ITaskTransitionController"""

    implements(ITaskTransitionController)

    def is_re_open_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer()

    def is_progress_to_resolve_possible(self):
        """see ITaskTransitionController"""

        return (self._is_responsible() and
                self._is_substasks_closed() and
                not self._is_unidirectional_by_value())

    def is_progress_to_closed_possible(self):
        """see ITaskTransitionController"""
        return (self._is_unidirectional_by_value() and
                self._is_substasks_closed())

    def is_cancel_possible(self):
        """see ITaskTransitionController"""
        return self._is_issuer()

    def is_open_to_progress_possible(self):
        """see ITaskTransitionController"""
        if not self._is_unidirectional_by_reference():
            if not self._is_issuer():
                return True
            elif self.context.issuer == self.context.responsible:
                return True
        return False

    def is_reject_possible(self):
        """see ITaskTransitionController"""
        return self._is_responsible()

    def is_open_to_resolve_possible(self):
        """see ITaskTransitionController"""
        if self._is_substasks_closed() and self._is_bidirectional():
            if not self._is_issuer():
                return True
            elif self.context.issuer == self.context.responsible:
                return True
        return False

    def is_open_to_close_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer() or self._is_unidirectional_by_reference()

    def is_rejected_to_open_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer()

    def is_resolve_to_open_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer()

    def is_resolve_to_closed_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer()

    def _is_issuer(self):
        """Checks if the actual user is the issuer of the
        actual task(actual context)"""

        return getMultiAdapter((self.context, self.request),
            name='plone_portal_state').member().id == self.context.issuer

    def _is_responsible(self):
        """Checks if the actual user is the issuer of the
        actual task(actual context)"""

        return getMultiAdapter((self.context, self.request),
            name='plone_portal_state').member().id == self.context.responsible

    def _is_substasks_closed(self):
        """Checks if all subtasks are done(resolve, cancelled or closed)"""

        wft = self.context.portal_workflow
        wf = wft.get(wft.getChainFor(self.context)[0])
        states = [s for s in wf.states]

        for state in TASK_CLOSED_STATES:
            states.pop(states.index(state))

        query = {
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': -1},
            'portal_type': 'opengever.task.task',
            'review_state': states}

        if len(self.context.getFolderContents(query)) > 1:
            return False
        else:
            return True

    def _is_unidirectional_by_value(self):
        """Check if the task.type is unidirectional_by_value"""
        return self.context.task_type_category == 'unidirectional_by_value'

    def _is_unidirectional_by_reference(self):
        """Check if the task.type is unidirectional_by_reference"""

        return self.context.task_type_category == 'unidirectional_by_reference'

    def _is_bidirectional(self):
        """see ITaskWorkflowChecks
        """
        categories = ['bidirectional_by_reference',
                      'bidirectional_by_value']
        return self.context.task_type_category in categories
