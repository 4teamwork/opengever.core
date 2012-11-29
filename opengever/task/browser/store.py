from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.task.browser.accept.utils import _get_yearfolder
from opengever.task.task import ITask
from opengever.task.util import change_task_workflow_state
from zExceptions import Unauthorized
import AccessControl


class StoreForwardingInYearfolderView(grok.View):
    grok.name('store_forwarding_in_yearfolder')
    grok.context(ITask)
    grok.require('zope2.View')

    def _check_permission(self):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        if not member.checkPermission('Add portal content', self.context):
            raise Unauthorized()

    def store_to_yearfolder(self,
                            text='',
                            transition='forwarding-transition-close',
                            successor_oguid=None):

        self._check_permission()

        inbox = aq_parent(aq_inner(self.context))
        yearfolder = _get_yearfolder(inbox)

        if transition:
            change_task_workflow_state(self.context,
                                      transition,
                                      text=text,
                                      successor_oguid=successor_oguid)

        try:
            # change security context
            _sm = AccessControl.getSecurityManager()
            AccessControl.SecurityManagement.newSecurityManager(
                    self.request,
                    AccessControl.SecurityManagement.SpecialUsers.system)

            clipboard = inbox.manage_cutObjects((self.context.getId(),))
            yearfolder.manage_pasteObjects(clipboard)

        except:
            AccessControl.SecurityManagement.setSecurityManager(
                _sm)
            raise
        else:
            AccessControl.SecurityManagement.setSecurityManager(
                _sm)

    def render(self):

        if self.is_already_done():
            # Set correct content type for text response
            self.request.response.setHeader("Content-type", "tex/plain")

            return 'OK'

        self.store_to_yearfolder(
            text=self.request.get('response_text'),
            transition=self.request.get('transition'),
            successor_oguid=self.request.get('successor_oguid'))

        # Set correct content type for text response
        self.request.response.setHeader("Content-type", "tex/plain")

        return 'OK'

    def is_already_done(self):
        """When the sender (caller of this view) has a conflict error, this
        view is called on the receiver multiple times, even when the changes
        are already done the first time. We need to detect such requests and
        tell the sender that it has worked.
        """

        parent = aq_parent(aq_inner(self.context))
        if parent.portal_type == 'opengever.inbox.yearfolder':
            return True
        else:
            return False
