from Acquisition import aq_inner, aq_parent
from five import grok
from opengever.task.browser.accept.utils import _get_yearfolder
from opengever.task.task import ITask
from opengever.task.util import change_task_workflow_state
import AccessControl


class StoreForwardingInYearfolderView(grok.View):
    grok.name('store_forwarding_in_yearfolder')
    grok.context(ITask)
    grok.require('cmf.AddPortalContent')

    def render(self):
        inbox = aq_parent(aq_inner(self.context))
        yearfolder = _get_yearfolder(inbox)
        successor_oguid = self.request.get('successor_oguid')
        transition = self.request.get('transition')
        response_text = self.request.get('response_text')

        if transition:
            change_task_workflow_state(self.context,
                                      transition,
                                      text=response_text,
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
            return 'OK'
