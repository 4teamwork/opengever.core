from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.task.browser.accept.utils import get_current_yearfolder
from opengever.task.interfaces import IYearfolderStorer
from opengever.task.task import ITask
import AccessControl


class YearfolderStorer(grok.Adapter):
    grok.provides(IYearfolderStorer)
    grok.context(ITask)

    def store_in_yearfolder(self):
        """Move the forwarding (adapted context) in the actual yearfolder."""

        inbox = aq_parent(aq_inner(self.context))
        yearfolder = get_current_yearfolder(inbox=inbox)

        try:
            # change security context
            _sm = AccessControl.getSecurityManager()
            AccessControl.SecurityManagement.newSecurityManager(
                    self.context.REQUEST,
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
