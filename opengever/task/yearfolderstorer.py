from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.base.security import changed_security
from opengever.document.handlers import DISABLE_DOCPROPERTY_UPDATE_FLAG
from opengever.task.browser.accept.utils import get_current_yearfolder
from opengever.task.interfaces import IYearfolderStorer
from opengever.task.task import ITask


class YearfolderStorer(grok.Adapter):
    grok.provides(IYearfolderStorer)
    grok.context(ITask)

    def store_in_yearfolder(self):
        """Move the forwarding (adapted context) in the actual yearfolder."""

        inbox = aq_parent(aq_inner(self.context))
        yearfolder = get_current_yearfolder(inbox=inbox)

        self.context.REQUEST.set(DISABLE_DOCPROPERTY_UPDATE_FLAG, True)

        with changed_security():
            clipboard = inbox.manage_cutObjects((self.context.getId(),))
            yearfolder.manage_pasteObjects(clipboard)
