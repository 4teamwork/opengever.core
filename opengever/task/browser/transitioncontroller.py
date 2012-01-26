from Products.Five import BrowserView
from opengever.task.interfaces import ISuccessorTaskController
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import Interface, implements

TASK_CLOSED_STATES = ['task-state-tested-and-closed',
                      'task-state-rejected',
                      'task-state-cancelled']


class ITaskTransitionController(Interface):
    """Interface for a controller view for checking,
    if certain transitions should be available or not"""

    def is_cancelled_to_open_possible():
        """Checks if:
        - The current user is the issuer of the current task(context)"""

    def is_progress_to_resolved_possible():
        """Checks if:
        - The task has no successors
        - Task is not unidirectional_by_value (zu direkten Erledigung).
        - The responsible is the current user or a inbox_group user.
        - All subtaskes are resolve, cancelled or closed.
        """

    def is_progress_to_closed_possible():
        """Checks if:
        - The task has no successors
        - Task is unidirectional_by_value (zu direkten Erledigung).
        - All subtaskes are resolved, cancelled or closed.
        """

    def is_cancel_possible():
        """Checks if:
        - The current user is the issuer."""

    def is_open_to_progress_possible():
        """Checks if ...
        - Not unidirectional_by_reference
        - The user is not the issuer, appart from he's also the responsible
        """

    def is_reject_possible():
        """Checks if ...
        - The current user is the responsible.
        """

    def is_open_to_resolved_possible():
        """Checks if:
        - All subtaskes are resolved, cancelled or closed.
        - The Task is is_bidirectional
        - The user is not the issuer, appart from he's also the responsible
        """

    def is_open_to_closed_possible():
        """Checks if:
        - The user is the issuer or is a unidirectional_byrefrence task"""

    def is_rejected_to_open_possible():
        """Checks if:
        - The current user is the issuer of the task"""

    def is_resolved_to_closed_possible():
        """Checks if:
        - The current user is the issuer of the task"""

    def is_resolved_to_progress_possible():
        """Checks if:
        - The current user is the issuer of the task"""


class TaskTransitionController(BrowserView):
    """Controller View: see ITaskTransitionController"""

    implements(ITaskTransitionController)

    def is_cancelled_to_open_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer()

    def is_progress_to_resolved_possible(self):
        """see ITaskTransitionController"""

        return (self._is_responsible_or_inbox_group_user() and
                self._is_substasks_closed() and
                not self._is_unidirectional_by_value() and
                (not self._has_successors() or self._is_remote_request()))

    def is_progress_to_closed_possible(self):
        """see ITaskTransitionController"""
        return (self._is_unidirectional_by_value() and
                self._is_substasks_closed() and
                (not self._has_successors() or self._is_remote_request()))

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

    def is_open_to_resolved_possible(self):
        """see ITaskTransitionController"""
        if self._is_substasks_closed() and self._is_bidirectional():
            if not self._is_issuer():
                return True
            elif self.context.issuer == self.context.responsible:
                return True
        return False

    def is_open_to_closed_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer() or self._is_unidirectional_by_reference()

    def is_rejected_to_open_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer()

    def is_resolved_to_closed_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer()

    def is_resolved_to_progress_possible(self):
        """see ITaskTransitionController"""

        return self._is_issuer()

    def _is_issuer(self):
        """Checks if the current user is the issuer of the
        current task(current context)"""

        return getMultiAdapter((self.context, self.request),
            name='plone_portal_state').member().id == self.context.issuer

    def _is_responsible(self):
        """Checks if the current user is the issuer of the
        current task(current context)"""

        return getMultiAdapter((self.context, self.request),
            name='plone_portal_state').member().id == self.context.responsible

    def _is_inbox_group_user(self):
        """Checks with the help of the contact information utility
        if the current user is in the inbox group"""

        info = getUtility(IContactInformation)
        return info.is_user_in_inbox_group(
            client_id=self.context.responsible_client)

    def _is_responsible_or_inbox_group_user(self):
        """Checks if the current user is the responsible
        or in the inbox_group"""

        return self._is_responsible() or self._is_inbox_group_user()

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

    def _is_remote_request(self):
        """checks if the current request cames from a remote client.
        For example a task over a mutliple clients."""

        if self.request.get_header('X-OGDS-CID', None):
            return True
        else:
            return False

    def _has_successors(self):
        """checks is the task has some successors
        """
        if ISuccessorTaskController(self.context).get_successors():
            return True
        return False
