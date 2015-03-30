from five import grok
from opengever.base.request import dispatch_request
from opengever.task.activities import TaskTransitionActivity
from opengever.task.browser.transitioncontroller import get_conditions
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.CMFDiffTool.utils import safe_utf8
from zExceptions import Unauthorized
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class DeadlineModifier(grok.Adapter):
    grok.context(ITask)
    grok.implements(IDeadlineModifier)

    def is_modify_allowed(self):
        """Check if the current user is allowed to modify the deadline:
        - state is `in-progress` or `open`
        - AND is issuer or is admin
        """

        # TODO: should be solved by a own permission 'modify_deadline'
        # but right now the issuer has not a sperate role.
        wft = getToolByName(self.context, 'portal_workflow')
        current_state = wft.getInfoFor(self.context, 'review_state')

        if current_state in ['task-state-open', 'task-state-in-progress']:
            return self._is_issuer_or_admin()
        return False

    def _is_issuer_or_admin(self):
        conditions = get_conditions(self.context)
        if conditions.is_issuer:
            return True
        elif self._is_administrator():
            return True

        return False

    def _is_administrator(self):
        """check if the user is a adminstrator or a manager"""

        current_user = api.user.get_current()
        if current_user.has_role('Administrator') or \
           current_user.has_role('Manager'):
            return True

        return False

    def modify_deadline(self, new_deadline, text, transition):
        """Handles the whole deadline mofication process:
        - Set the new deadline
        - Add response
        - Handle synchronisation if needed
        """

        if not self.is_modify_allowed():
            raise Unauthorized

        self.update_deadline(new_deadline, text, transition)
        self.sync_deadline(new_deadline, text, transition)

    def update_deadline(self, new_deadline, text, transition):
        response = add_simple_response(
            self.context, text=text,
            field_changes=(
                (ITask['deadline'], new_deadline),
            ),
            transition=transition
        )

        self.record_activity(response)

        self.context.deadline = new_deadline
        notify(ObjectModifiedEvent(self.context))

    def record_activity(self, response):
        TaskTransitionActivity(self.context, response).record()

    def sync_deadline(self, new_deadline, text, transition):
        sct = ISuccessorTaskController(self.context)
        for successor in sct.get_successors():

            response = dispatch_request(
                successor.admin_unit_id,
                '@@remote_deadline_modifier',
                successor.physical_path,
                data={
                    'new_deadline': new_deadline.toordinal(),
                    'text': safe_utf8(text),
                    'transition': transition})

            if response.read().strip() != 'OK':
                raise Exception(
                    'Updating deadline on remote client %s. failed (%s)' % (
                        successor.admin_unit_id, response.read()))
