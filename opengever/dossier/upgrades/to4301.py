from ftw.upgrade import UpgradeStep


class AddSablonTemplatesTab(UpgradeStep):

    def __call__(self):
        self.actions_add_type_action(
            'opengever.dossier.templatedossier',
            after='documents',
            action_id='sablontemplates',
            **{'title': 'Sablon Templates',
               'action': 'string:#',
               'category': 'tabbedview-tabs',
               'condition': 'object/@@is_meeting_feature_enabled',
               'link_target': '',
               'visible': True,
               'permissions': ('View', )})
