from opengever.task import FINAL_TASK_STATES
from opengever.task import is_optional_task_permissions_revoking_enabled
from opengever.task.localroles import LocalRolesSetter
from opengever.task.task import ITask
from plone import api
from Products.Five.browser import BrowserView
from zExceptions import Unauthorized
from opengever.task import _


class RevokePermissions(BrowserView):

    def __call__(self):
        if not self.is_available():
            raise Unauthorized()
        LocalRolesSetter(self.context).revoke_roles()

        return self.redirect()

    def is_available(self):
        """The action should only be available on closed tasks for
        administrators and task issuer and only if the feature is enabled.
        """
        if not is_optional_task_permissions_revoking_enabled():
            return False
        if not ITask.providedBy(self.context):
            return False
        if not self.context.get_review_state() in FINAL_TASK_STATES:
            return False
        if api.user.has_permission('cmf.ManagePortal'):
            return True
        issuer = self.context.get_issuer_actor()
        return issuer.identifier == api.user.get_current().id

    def redirect(self):
        """Redirects to task if the current user still has View permission,
        otherwise it redirects to portal.
        """
        if not api.user.has_permission('View', obj=self.context):
            msg = _(u'msg_revoking_successful_no_longer_permission_to_access',
                    default=u'Permissions have been succesfully revoked, '
                    'you are no longer permitted to access the task.')
            api.portal.show_message(msg, request=self.request, type='info')
            url = api.portal.get().absolute_url()
        else:
            msg = _(u'msg_revoking_successful',
                    default=u'Permissions have been succesfully revoked')
            api.portal.show_message(msg, request=self.request, type='info')
            url = self.context.absolute_url()

        return self.request.RESPONSE.redirect(url)
