from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.disposition.interfaces import IDisposition
from zope.component import adapter


@adapter(IDisposition, IOpengeverBaseLayer)
class DispositionContextActions(BaseContextActions):

    def is_download_appraisal_list_available(self):
        return True

    def is_download_removal_protocol_available(self):
        return self.context.removal_protocol_available()

    def is_download_sip_available(self):
        return self.context.sip_download_available()
