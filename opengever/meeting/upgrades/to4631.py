from ftw.upgrade import UpgradeStep


class ShowSablonTemplateVersionsTab(UpgradeStep):

    def __call__(self):
        self.actions_add_type_action(
            'opengever.meeting.sablontemplate',
            after='overview',
            action_id='versions',
            **{'title': 'Versions',
               'action': 'string:#',
               'category': 'tabbedview-tabs',
               'condition': '',
               'link_target': '',
               'visible': True,
               'permissions': tuple(),
               })
