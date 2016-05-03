from five import grok
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition import _
from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IHistoryStorage
from opengever.tabbedview.browser.base import OpengeverTab
from plone import api
from plone.protect.utils import addTokenToUrl
import json


class DispositionOverview(grok.View, OpengeverTab):
    grok.context(IDisposition)
    grok.name('tabbedview_view-overview')
    grok.require('zope2.View')
    grok.template('overview')

    show_searchform = False

    def get_dossiers(self):
        return self.context.get_dossier_representations()

    def is_archival_worthy(self, dossier):
        return ILifeCycle(dossier).archival_value != ARCHIVAL_VALUE_UNWORTHY

    def get_localized_time(self, value):
        return api.portal.get_localized_time(datetime=value)

    def get_update_appraisal_url(self, dossier, appraisal):
        url = '{}/update_appraisal_view?dossier-id={}&appraisal={}'.format(
            self.context.absolute_url(), dossier.intid, json.dumps(appraisal))

        return addTokenToUrl(url)

    def get_transitions(self):
        wftool = api.portal.get_tool(name='portal_workflow')
        infos = wftool.listActionInfos(object=self.context, check_condition=False)
        return infos

    def get_actions(self):
        return [
            {'id': 'export_appraisal_list',
             'label': _('label_export_appraisal_list',
                        default=u'Export appraisal list'),
             'url': '{}/xlsx'.format(self.context.absolute_url()),
             'visible': True,
             'class': 'appraisal_list'},
            {'id': 'sip_download',
             'label': _('label_sip_download', default=u'SIP download'),
             'url': '{}/ech0160_export'.format(self.context.absolute_url()),
             'visible': self.sip_download_available(),
             'class': 'sip_download'},
        ]

    def sip_download_available(self):
        """TODO: Should be protected with a own permission.
        """
        return api.content.get_state(self.context) == 'disposition-state-disposed'

    def appraisal_buttons_available(self):
        return api.content.get_state(self.context) == 'disposition-state-in-progress'

    def get_history(self):
        return IHistoryStorage(self.context).get_history()
