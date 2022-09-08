from AccessControl.requestmethod import postonly
from AccessControl.SecurityInfo import ClassSecurityInfo
from logging import getLogger
from OFS.Cache import Cacheable
from opengever.ogds.models.group import Group
from opengever.ogds.models.group import groups_users
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from Products.CMFCore.permissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IGroupEnumerationPlugin  # noqa
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin  # noqa
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from sqlalchemy.sql import select
from zope.interface import implements


logger = getLogger('OGDSAuthenticationPlugin')


manage_addOGDSAuthenticationPlugin = PageTemplateFile(
    "www/addPlugin", globals(), __name__="manage_addOGDSAuthenticationPlugin")


def addOGDSAuthenticationPlugin(self, id_, title=None, REQUEST=None):
    """Add an OGDS authentication plugin
    """
    plugin = OGDSAuthenticationPlugin(id_, title)
    self._setObject(plugin.getId(), plugin)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
            '{}/manage_workspace'
            '?manage_tabs_message=OGDS+authentication+plugin+added.'.format(
                self.absolute_url()))


class OGDSAuthenticationPlugin(BasePlugin, Cacheable):
    """Plone PAS plugin for authentication against OGDS.
    """
    implements(
        IUserEnumerationPlugin,
        IGroupEnumerationPlugin,
        IGroupsPlugin,
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

        results = ()

        if login and (not id):
            id = login

        query = (
            select([User.userid])
            .where(User.active == True)
            .order_by(User.userid)
        )

        if exact_match:
            if not id:
                raise ValueError('Exact match specified but no ID or login given')
            query = query.where(User.userid == id)
        elif id:
            pattern = '%{}%'.format(id)
            query = query.where(User.userid.ilike(pattern))

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

        query = (
            select([Group.groupid])
            .where(Group.active == True)
            .order_by(Group.groupid)
        )

        if exact_match:
            if not id:
                raise ValueError('Exact match specified but no ID given')
            query = query.where(Group.groupid == id)
        elif id:
            pattern = '%{}%'.format(id)
            query = query.where(Group.groupid.ilike(pattern))

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

        groups = Group.__table__
        query = (
            select([groups.c.groupid])
            .select_from(groups.join(groups_users))
            .where(groups_users.c.userid == principal_id)
            .where(groups.c.active == True)
        )
        results = tuple([
            groupid.encode('utf-8')
            for groupid, in self.query_ogds(query)
        ])

        self.ZCacheable_set(results, view_name=view_name, keywords=criteria)
        self.log('Found groups: {!r}'.format(results))
        return results

    security.declareProtected(ManagePortal, 'manage_updateConfig')

    @postonly
    def manage_updateConfig(self, REQUEST):
        """Update configuration of OGDS Authentication Plugin.
        """
        response = REQUEST.response

        self.debug_mode = REQUEST.form.get('debug_mode', False)

        response.redirect('{}/manage_config?manage_tabs_message={}'.format(
                          self.absolute_url(), 'Configuration+updated.'))
