from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import remote_request
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.component import getUtility
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
        member = getMultiAdapter((self.context, self.context.REQUEST),
                                    name='plone_portal_state').member()

        return bool(self._is_issuer(member) or self._is_administrator(member))

    def _is_issuer(self, member):
        """Checks if the current user is the issuer of the
        current task(current context)"""

        info = getUtility(IContactInformation)

        if not info.is_inbox(self.context.issuer):
            return bool(member.id == self.context.issuer)
        else:
            return info.is_group_member(
                info.get_groupid_of_inbox(self.context.issuer),
                member.id)

    def _is_administrator(self, member):
        """check if the user is a adminstrator"""

        return member.has_role('Administrator') or member.has_role('Manager')

    def modify_deadline(self, new_deadline, text):
        """Handles the whole deadline mofication process:
        - Set the new deadline
        - Add response
        - Handle synchronisation if needed
        """

        if not self.is_modify_allowed():
            raise Unauthorized

        self.update_deadline(new_deadline, text)
        self.sync_deadline(new_deadline, text)

    def update_deadline(self, new_deadline, text):
        add_simple_response(
            self.context, text=text,
            field_changes=(
                (ITask['deadline'], new_deadline),
            ),
        )

        self.context.deadline = new_deadline
        notify(ObjectModifiedEvent(self.context))

    def sync_deadline(self, new_deadline, text):
        sct = ISuccessorTaskController(self.context)
        for successor in sct.get_successors():

            response = remote_request(
                successor.admin_unit_id,
                '@@remote_deadline_modifier',
                successor.physical_path,
                data={
                    'new_deadline': new_deadline.toordinal(),
                    'text': text})

            if response.read().strip() != 'OK':
                raise Exception(
                    'Updating deadline on remote client %s. failed (%s)' % (
                        successor.client_id, response.read()))
