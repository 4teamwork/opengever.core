from five import grok
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition.interfaces import IDisposition
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

    def get_update_appraisal_url(self, dossier, should_be_archived):
        url = '{}/update_appraisal_view?dossier-id={}&should_be_archived={}'.format(
            self.context.absolute_url(), dossier.intid, json.dumps(should_be_archived))

        return addTokenToUrl(url)

    def get_transitions(self):
        wftool = api.portal.get_tool(name='portal_workflow')
        infos = wftool.listActionInfos(object=self.context, check_condition=False)
        return infos
