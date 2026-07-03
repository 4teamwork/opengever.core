from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.disposition import is_sip_archive_delivery_enabled
from opengever.disposition.interfaces import IDisposition
from plone import api
from zope.component import adapter


@adapter(IDisposition, IOpengeverBaseLayer)
class DispositionContextActions(BaseContextActions):

    def get_actions(self):
        super(DispositionContextActions, self).get_actions()
        self.maybe_add_sip_archive_delivery()
        return self.actions

    def is_download_appraisal_list_available(self):
        return True

    def is_download_removal_protocol_available(self):
        return self.context.removal_protocol_available()

    def is_download_sip_available(self):
        return self.context.sip_download_available()

    def maybe_add_sip_archive_delivery(self):
        if not is_sip_archive_delivery_enabled():
            return False
        if not api.user.has_permission('opengever.disposition: Download SIP Package', obj=self.context):
            return False
        if not self.context.has_sip_package():
            return False

        self.add_action(u'sip-archive-delivery')
