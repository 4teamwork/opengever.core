from ftw.upgrade import UpgradeStep
from Products.CMFPlone.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
import logging

LOG = logging.getLogger('ftw.upgrade')


class ActivateGroupsPluginForSourceGroups(UpgradeStep):
    """Activate groups plugin for source groups.

    The groups plugin determines the groups to which a user belongs. This is
    mandatory to make permission lookups through groups possible.

    Since an admin can manage local groups, we need to activate this plugin
    for the source_groups.
    """

    def __call__(self):
        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins

        # Make sure that source_groups is activated for groups plugin
        groups_plugin = plugins.getAllPlugins('IGroupsPlugin')
        if 'source_groups' in groups_plugin.get('available'):
            plugins.activatePlugin(IGroupsPlugin, 'source_groups')
        elif 'source_groups' not in groups_plugin.get('active'):
            LOG.error('Source groups is not available for group introspection')

        # move source_groups plugin up. 3 times...
        plugins.movePluginsUp(IGroupsPlugin, ('source_groups',))
        plugins.movePluginsUp(IGroupsPlugin, ('source_groups',))
        plugins.movePluginsUp(IGroupsPlugin, ('source_groups',))
