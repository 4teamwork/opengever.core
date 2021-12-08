from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.disposition import _
from plone import api
from plone.protect.utils import addTokenToUrl
from Products.Five.browser import BrowserView


class DispositionOverview(BrowserView):

    def __call__(self):
        self.init_dossiers()
        return super(DispositionOverview, self).__call__()

    def init_dossiers(self):
        self.active_dossiers, self.inactive_dossiers = \
            self.context.get_grouped_dossier_representations()

    def _add_to(self, mapping, dossier):
        key = dossier.get_grouping_key()
        mapping.setdefault(key, []).append(dossier)

    def get_dossier_lists(self):
        return [
            [_(u'label_resolved_dossiers', default=u'Resolved Dossiers'),
             self.active_dossiers],
            [_(u'label_inactive_dossiers', default=u'Inactive Dossiers'),
             self.inactive_dossiers]
        ]

    def is_archival_worthy(self, dossier):
        return ILifeCycle(dossier).archival_value != ARCHIVAL_VALUE_UNWORTHY

    def get_localized_time(self, value):
        return api.portal.get_localized_time(datetime=value)

    def get_update_appraisal_url(self):
        return addTokenToUrl(
            '{}/update_appraisal_view'.format(self.context.absolute_url()))

    def get_transitions(self):
        wftool = api.portal.get_tool(name='portal_workflow')
        infos = wftool.listActionInfos(object=self.context, check_condition=False)
        return infos

    def get_actions(self):
        return [
            {'id': 'export_appraisal_list',
             'label': _('label_export_appraisal_list_as_excel',
                        default=u'Export appraisal list as excel'),
             'url': '{}/download_excel'.format(self.context.absolute_url()),
             'visible': True,
             'class': 'appraisal_list'},
            {'id': 'sip_download',
             'label': _('label_dispositon_package_download',
                        default=u'Download disposition package'),
             'url': '{}/ech0160_download'.format(self.context.absolute_url()),
             'visible': self.context.sip_download_available(),
             'class': 'sip_download'},
            {'id': 'removal_protocol',
             'label': _('label_download_removal_protocol',
                        default=u'Download removal protocol'),
             'url': '{}/removal_protocol'.format(self.context.absolute_url()),
             'visible': self.context.removal_protocol_available(),
             'class': 'removal_protocol'}
        ]

    def sip_store_available(self):
        return api.user.has_permission(
            'opengever.disposition: Download SIP Package',
            obj=self.context)

    def appraisal_buttons_available(self):
        return api.content.get_state(self.context) == 'disposition-state-in-progress'

    def get_history(self):
        return self.context.get_history()

    def get_states(self):
        """Returns a sorted list of all disposition states.
        Used to generate and display the status wizard.
        """

        return ['disposition-state-in-progress',
                'disposition-state-appraised',
                'disposition-state-disposed',
                'disposition-state-archived',
                'disposition-state-closed']

    def get_current_state(self):
        return api.content.get_state(self.context)

    def update_transfer_number_url(self):
        return '{}/update-transfer-number'.format(self.context.absolute_url())

    def is_transfer_number_editable(self):
        return api.user.has_permission(
            'opengever.disposition: Edit transfer number', obj=self.context)
