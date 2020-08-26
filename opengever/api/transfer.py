from opengever.inbox.forwarding import IForwarding
from opengever.ogds.models.user import User
from opengever.task.activities import TaskChangeIssuerActivity
from opengever.task.activities import TaskReassignActivity
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.localroles import LocalRolesSetter
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectModifiedEvent


class ExtractOldNewUserMixin(Service):
    """This mixin privdes a method to extract and validate the old and the new
    userid from the request body.
    """
    def extract_userids(self):
        data = json_body(self.request)
        old_userid = data.get("old_userid")
        new_userid = data.get("new_userid")

        if not old_userid:
            raise BadRequest("Property 'old_userid' is required")
        if not new_userid:
            raise BadRequest("Property 'new_userid' is required")
        if not User.query.get_by_userid(old_userid):
            raise BadRequest("userid '{}' does not exist".format(old_userid))
        if not User.query.get_by_userid(new_userid):
            raise BadRequest("userid '{}' does not exist".format(new_userid))
        if old_userid == new_userid:
            raise BadRequest("'old_userid' and 'new_userid' should not be the same")

        return old_userid, new_userid


class TransferTaskPost(ExtractOldNewUserMixin, Service):
    def reply(self):
        self.old_userid, self.new_userid = self.extract_userids()

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        task_controller = ISuccessorTaskController(self.context)
        if task_controller.get_predecessor() or task_controller.get_successors():
            raise BadRequest("Cross-client tasks cannot be transferred")

        self.request.environ['HTTP_X_GEVER_SUPPRESSNOTIFICATIONS'] = 'True'

        if IForwarding.providedBy(self.context):
            responsible_transition = 'forwarding-transition-reassign'
            issuer_transition = 'forwarding-transition-change-issuer'
        else:
            responsible_transition = 'task-transition-reassign'
            issuer_transition = 'task-transition-change-issuer'

        if self.context.revoke_permissions:
            LocalRolesSetter(self.context).revoke_roles()

        self.context.clear_reminder(self.old_userid)

        issuer_changed = self.old_userid == self.context.issuer
        responsible_changed = self.old_userid == self.context.responsible

        if issuer_changed:
            issuer_changes = [(ITask['issuer'], self.new_userid)]
            issuer_response = add_simple_response(
                        self.context, transition=issuer_transition,
                        field_changes=issuer_changes,
                        supress_events=True)
            self.context.issuer = self.new_userid

        if responsible_changed:
            responsible_changes = [(ITask['responsible'], self.new_userid)]
            responsible_response = add_simple_response(
                        self.context, transition=responsible_transition,
                        field_changes=responsible_changes,
                        supress_events=True)
            self.context.responsible = self.new_userid

        if issuer_changed or responsible_changed:
            notify(ObjectModifiedEvent(self.context))

        if issuer_changed:
            TaskChangeIssuerActivity(self.context, self.context.REQUEST, issuer_response).record()
        if responsible_changed:
            TaskReassignActivity(self.context, self.context.REQUEST, responsible_response).record()

        self.request.response.setStatus(204)
        return super(TransferTaskPost, self).reply()
