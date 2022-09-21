from AccessControl.requestmethod import postonly
from AccessControl.SecurityInfo import ClassSecurityInfo
from logging import getLogger
from OFS.Cache import Cacheable
from opengever.ogds.models.group import Group
from opengever.ogds.models.group import groups_users
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from plone import api
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.utils import safe_unicode
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IGroupEnumerationPlugin  # noqa
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin  # noqa
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from sqlalchemy import func
from sqlalchemy.sql import select
from zope.interface import implements


logger = getLogger('OGDSAuthenticationPlugin')


manage_addOGDSAuthenticationPlugin = PageTemplateFile(
    "www/addPlugin", globals(), __name__="manage_addOGDSAuthenticationPlugin")


def addOGDSAuthenticationPlugin(self, id_, title=None, REQUEST=None):
    """Add an OGDS authentication plugin
    """
    configure_after_creation = bool(
        REQUEST.form.get('configure_after_creation', False))

    install_ogds_auth_plugin(id_, title, configure_after_creation)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
            '{}/manage_workspace'
            '?manage_tabs_message=OGDS+authentication+plugin+added.'.format(
                self.absolute_url()))


def install_ogds_auth_plugin(id_='ogds_auth', title=None,
                             configure_after_creation=True):
    acl_users = api.portal.get_tool('acl_users')

    if id_ not in acl_users.objectIds():
        plugin = OGDSAuthenticationPlugin(id_, title)
        acl_users._setObject(plugin.getId(), plugin)
        plugin = acl_users[plugin.getId()]

        if configure_after_creation:
            plugin.ZCacheable_setManagerId('RAMCache')

            plugin.manage_activateInterfaces([
                'IUserEnumerationPlugin',
                'IGroupEnumerationPlugin',
                'IGroupsPlugin',
                'IPropertiesPlugin',
            ])

            # Move properties plugin to top position
            while not acl_users.plugins.listPluginIds(IPropertiesPlugin)[0] == plugin.getId():
                acl_users.plugins.movePluginsUp(IPropertiesPlugin, [plugin.getId()])


class OGDSAuthenticationPlugin(BasePlugin, Cacheable):
    """Plone PAS plugin to enumerate users and groups from OGDS.

    This plugin aims to replace parts of the functionality provided by the
    LDAP/AD plugins from P.LDAPMultiPlugins, so that we can eventually
    remove those from our stack.

    It acts as a user/group source backed by OGDS, capable of enumerating
    users, groups, group memberships and properties.

    This plugin does not perform authentication itself, but instead requires
    there to be some other IAuthenticationPlugin that is capable of
    authenticating users for this deployment (e.g. cas_auth).
    """
    implements(
        IUserEnumerationPlugin,
        IGroupEnumerationPlugin,
        IGroupsPlugin,
        IPropertiesPlugin,
    )
    meta_type = 'OGDS Authentication Plugin'
    security = ClassSecurityInfo()

    # ZMI tab for configuration page
    manage_options = (
        ({'label': 'Configuration',
          'action': 'manage_config'},)
        + BasePlugin.manage_options
        + Cacheable.manage_options
    )
    security.declareProtected(ManagePortal, 'manage_config')
    manage_config = PageTemplateFile('www/config', globals(),
                                     __name__='manage_config')

    # Supported properties for search and enumeration
    USER_PROPS = {
        'userid': User.userid,
        'email': User.email,
        'firstname': User.firstname,
        'lastname': User.lastname,
        'fullname': (User.firstname + u' ' + User.lastname),
    }
    GROUP_PROPS = {
        'groupid': Group.groupid,
        'title': Group.title,
    }

    def __init__(self, id_, title=None):
        self._setId(id_)
        self.title = title
        self.debug_mode = False

    @staticmethod
    def query_ogds(query):
        return ogds_service().session.execute(query)

    def log(self, msg):
        if self.debug_mode:
            logger.info(msg)

    def to_ascii(self, value):
        try:
            return value.encode('ascii')
        except UnicodeEncodeError:
            return None

    def known_properties(self, principal_type):
        if principal_type == 'user':
            return self.USER_PROPS.keys()
        else:
            return self.GROUP_PROPS.keys()

    security.declarePrivate('enumerateUsers')

    # IUserEnumerationPlugin implementation
    def enumerateUsers(self, id=None, login=None, exact_match=False,
                       sort_by=None, max_results=None, **kw):
        self.log('Enumerating users for id={!r}, login={!r}'.format(id, login))

        view_name = self.getId() + '_enumerateUsers'
        criteria = {
            'id': id,
            'login': login,
            'exact_match': exact_match,
            'sort_by': sort_by,
            'max_results': max_results,
        }
        criteria.update(kw)
        cached_info = self.ZCacheable_get(
            view_name=view_name, keywords=criteria, default=None)

        if cached_info is not None:
            self.log('Returning cached results from enumerateUsers()')
            return cached_info

        if 'name' in kw and login:
            # This is most likely the sharing view searching for a user by "id"
            # It never queries by 'id', only by 'login' plus 'name' (which is
            # not an OGDS column or property we support). By just dropping
            # the 'name' criterion we essentially turn this into a lookup by
            # login which then succeeds.
            del kw['name']

        # Unknown search critera - must not return any results
        if any((key not in self.known_properties('user') for key in kw)):
            self.ZCacheable_set((), view_name=view_name, keywords=criteria)
            return ()

        results = ()

        if login and (not id):
            id = login

        id = safe_unicode(id)
        for key, value in kw.items():
            kw[key] = safe_unicode(value)

        query = (
            select([User.userid])
            .where(User.active == True)
            .order_by(User.userid)
        )

        if exact_match:
            if not (id or kw):
                raise ValueError('Exact match specified but no criteria given')
            if id:
                query = query.where(func.lower(User.userid) == id.lower())

            for key, value in kw.items():
                column = self.USER_PROPS.get(key)
                if column is not None:
                    query = query.where(func.lower(column) == value.lower())

        else:
            if id:
                pattern = u'%{}%'.format(id)
                query = query.where(User.userid.ilike(pattern))

            for key, value in kw.items():
                column = self.USER_PROPS.get(key)
                if column is not None:
                    pattern = u'%{}%'.format(value)
                    query = query.where(column.ilike(pattern))

        if isinstance(max_results, int):
            query = query.limit(max_results)

        matches = [
            userid.encode('utf-8')
            for userid, in self.query_ogds(query)
        ]
        plugin_id = self.getId()
        results = tuple(({
            'id': userid,
            'login': userid,
            'pluginid': plugin_id,
        } for userid in matches))

        # This caching is not as effective yet as it could be:
        # Because we just store results (all users) for id=None, login=None
        # queries with the cache key for "no id/login criteria" , a subsequent
        # query for any single user will still result in a cache miss.
        #
        # We could improve this by iterating over results in this case, and
        # also cache each individual user record with its individual cache key.

        self.ZCacheable_set(results, view_name=view_name, keywords=criteria)
        self.log('Found users: {!r}'.format([user['id'] for user in results]))
        return results

    security.declarePrivate('enumerateGroups')

    # IGroupEnumerationPlugin implementation
    def enumerateGroups(self, id=None, exact_match=False, sort_by=None,
                        max_results=None, **kw):
        self.log('Enumerating groups for id={!r}'.format(id))

        view_name = self.getId() + '_enumerateGroups'
        criteria = {
            'id': id,
            'exact_match': exact_match,
            'sort_by': sort_by,
            'max_results': max_results,
        }
        criteria.update(kw)
        cached_info = self.ZCacheable_get(
            view_name=view_name, keywords=criteria, default=None)

        if cached_info is not None:
            self.log('Returning cached results from enumerateGroups()')
            return cached_info

        # Unknown search critera - must not return any results
        if any((key not in self.known_properties('group') for key in kw)):
            self.ZCacheable_set((), view_name=view_name, keywords=criteria)
            return ()

        id = safe_unicode(id)
        for key, value in kw.items():
            kw[key] = safe_unicode(value)

        query = (
            select([Group.groupid])
            .where(Group.active == True)
            .order_by(Group.groupid)
        )

        if exact_match:
            if not (id or kw):
                raise ValueError('Exact match specified but no criteria given')
            if id:
                query = query.where(func.lower(Group.groupid) == id.lower())

            for key, value in kw.items():
                column = self.GROUP_PROPS.get(key)
                if column:
                    query = query.where(func.lower(column) == value.lower())

        else:
            if id:
                pattern = u'%{}%'.format(id)
                query = query.where(Group.groupid.ilike(pattern))

            for key, value in kw.items():
                column = self.GROUP_PROPS.get(key)
                if column:
                    pattern = u'%{}%'.format(value)
                    query = query.where(column.ilike(pattern))

        if isinstance(max_results, int):
            query = query.limit(max_results)

        matches = [
            groupid.encode('utf-8')
            for groupid, in self.query_ogds(query)
        ]

        plugin_id = self.getId()
        results = tuple(({
            'id': groupid,
            'pluginid': plugin_id,
        } for groupid in matches))

        self.ZCacheable_set(results, view_name=view_name, keywords=criteria)
        self.log('Found groups: {!r}'.format([group['id'] for group in results]))
        return results

    security.declarePrivate('getGroupsForPrincipal')

    # IGroupsPlugin implementation
    def getGroupsForPrincipal(self, principal, request=None):
        self.log('Getting groups for principal={!r}'.format(principal))

        view_name = self.getId() + '_getGroupsForPrincipal'
        principal_id = principal.getId()
        criteria = {'id': principal_id}
        cached_info = self.ZCacheable_get(
            view_name=view_name, keywords=criteria, default=None)

        if cached_info is not None:
            self.log('Returning cached results from getGroupsForPrincipal()')
            return cached_info

        principal_id = safe_unicode(principal_id)

        groups = Group.__table__
        query = (
            select([groups.c.groupid])
            .select_from(groups.join(groups_users))
            .where(func.lower(groups_users.c.userid) == principal_id.lower())
            .where(groups.c.active == True)
        )

        # Omit groups with non-ASCII names
        results = tuple(filter(None, [
            self.to_ascii(groupid)
            for groupid, in self.query_ogds(query)
        ]))

        self.ZCacheable_set(results, view_name=view_name, keywords=criteria)
        self.log('Found groups: {!r}'.format(results))
        return results

    security.declarePrivate('getPropertiesForUser')

    # IPropertiesPlugin implementation
    def getPropertiesForUser(self, user, request=None):
        self.log('Getting properties for user={!r}'.format(user))

        view_name = self.getId() + '_getPropertiesForUser'
        principal_id = user.getId()
        is_group = user.isGroup()
        criteria = {
            'id': principal_id,
            'is_group': is_group,
        }
        cached_info = self.ZCacheable_get(
            view_name=view_name, keywords=criteria, default=None)

        if cached_info is not None:
            self.log('Returning cached results from getPropertiesForUser()')
            return cached_info

        principal_id = safe_unicode(principal_id)

        supported_props = self.USER_PROPS
        id_column = User.userid
        active_column = User.active

        if is_group:
            supported_props = self.GROUP_PROPS
            id_column = Group.groupid
            active_column = Group.active

        properties = {}
        prop_keys, prop_columns = (
            supported_props.keys(), supported_props.values())
        query = (
            select(prop_columns)
            .where(func.lower(id_column) == principal_id.lower())
            .where(active_column == True)
        )
        match = self.query_ogds(query).fetchone()

        if match:
            properties = dict(zip(
                prop_keys,
                [value.encode('utf-8') if value else '' for value in match]
            ))

            self.log("Returning properties %r" % properties)

        self.ZCacheable_set(properties, view_name=view_name, keywords=criteria)
        return properties

    security.declareProtected(ManagePortal, 'manage_updateConfig')

    @postonly
    def manage_updateConfig(self, REQUEST):
        """Update configuration of OGDS Authentication Plugin.
        """
        response = REQUEST.response

        self.debug_mode = REQUEST.form.get('debug_mode', False)

        response.redirect('{}/manage_config?manage_tabs_message={}'.format(
                          self.absolute_url(), 'Configuration+updated.'))
