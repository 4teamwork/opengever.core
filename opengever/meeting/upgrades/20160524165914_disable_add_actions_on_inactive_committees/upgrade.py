from ftw.upgrade import UpgradeStep
from plone import api
from Products.CMFCore.Expression import Expression


class DisableAddActionsOnInactiveCommittees(UpgradeStep):
    """Disable Add actions on inactive Committees.
    """

    action_ids = ['add-meeting', 'add-membership']
    condition_expr = Expression('context/is_active')

    def __call__(self):
        self.install_upgrade_profile()

        ttool = api.portal.get_tool('portal_types')
        fti = ttool.get('opengever.meeting.committee')

        for action in fti._actions:
            if action.id in self.action_ids:
                action.condition = self.condition_expr
