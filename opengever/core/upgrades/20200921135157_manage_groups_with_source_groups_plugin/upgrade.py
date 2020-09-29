from ftw.upgrade import UpgradeStep
from Products.CMFPlone.utils import getToolByName
from Products.PlonePAS.interfaces.group import IGroupIntrospection
from Products.PlonePAS.interfaces.group import IGroupManagement
from Products.PluggableAuthService.interfaces.plugins import IGroupEnumerationPlugin
import logging

LOG = logging.getLogger('ftw.upgrade')


class ManageGroupsWithSourceGroupsPlugin(UpgradeStep):
    """Manage groups with source groups plugin.
    """

    def __call__(self):
        """
        Manage groups with source groups plugin and not with ldap plugin.
        As we now overwrite the @groups endpoint allowing also admin to manage
        groups, we want to avoid mistakingly writing in the ldap. Managed groups
        should all be source groups. For that we move the source_groups plugin
        to the top.
        We now also need to find the created source groups, hence we need to
        activate enumeration and  introspection for the source_groups plugin.
        """
        acl_users = getToolByName(self.portal, 'acl_users')
        plugins = acl_users.plugins
        group_management_plugins = plugins.getAllPlugins('IGroupManagement')

        if 'source_groups' in group_management_plugins.get('available'):
            plugins.activatePlugin(IGroupManagement, 'source_groups')
        elif 'source_groups' not in group_management_plugins.get('active'):
            LOG.error('Source groups is not available for group management')

        # move source_groups plugin up. 3 times... why not!
        plugins.movePluginsUp(IGroupManagement, ('source_groups',))
        plugins.movePluginsUp(IGroupManagement, ('source_groups',))
        plugins.movePluginsUp(IGroupManagement, ('source_groups',))

        # check that source_groups is now in first position for group management
        group_management_plugins = plugins.getAllPlugins('IGroupManagement')
        if 'source_groups' in group_management_plugins.get('active') and not \
           group_management_plugins.get('active')[0] == 'source_groups':
            LOG.error('Source groups plugin could not be moved to top of group'
                      ' management plugins')

        # Make sure that source_groups is activated for group enumeration
        group_enumeration_plugins = plugins.getAllPlugins('IGroupEnumerationPlugin')
        if 'source_groups' in group_enumeration_plugins.get('available'):
            plugins.activatePlugin(IGroupEnumerationPlugin, 'source_groups')
        elif 'source_groups' not in group_enumeration_plugins.get('active'):
            LOG.error('Source groups is not available for group enumeration')

        # Make sure that source_groups is activated for  group introspection
        group_introspecion_plugins = plugins.getAllPlugins('IGroupIntrospection')
        if 'source_groups' in group_introspecion_plugins.get('available'):
            plugins.activatePlugin(IGroupIntrospection, 'source_groups')
        elif 'source_groups' not in group_introspecion_plugins.get('active'):
            LOG.error('Source groups is not available for group introspection')
