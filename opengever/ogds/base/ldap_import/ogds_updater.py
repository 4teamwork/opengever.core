from five import grok
from ldap import NO_SUCH_OBJECT
from opengever.ogds.base.interfaces import ILDAPSearch
from opengever.ogds.base.interfaces import IOGDSUpdater
from opengever.ogds.base.utils import create_session
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin


class OGDSUpdater(grok.Adapter):
    """Adapter to synchronize users and groups from LDAP into OGDS.
    """
    grok.provides(IOGDSUpdater)
    grok.context(IPloneSiteRoot)

    def __init__(self, context):
        self.context = context

    def get_sql_user(self, userid):
        """Returns the OGDS user object identified by `userid`.
        """
        session = create_session()
        return session.query(User).filter_by(userid=userid).first()

    def user_exists(self, userid):
        """Checks whether the OGDS user identified by `userid` exists or not.
        """
        session = create_session()
        return session.query(User).filter_by(userid=userid).count() != 0

    def group_exists(self, groupid):
        """Checks whether the OGDS group identified by `groupid` exists or not.
        """
        session = create_session()
        return session.query(Group).filter_by(groupid=groupid).count() != 0

    def _ldap_plugins(self):
        ldap_plugins = []
        for item in self.context['acl_users'].objectValues():
            if ILDAPMultiPlugin.providedBy(item):
                ldap_plugins.append(item)
        return ldap_plugins

    def import_users(self):
        """Imports users from all the configured LDAP plugins into OGDS.
        """
        session = create_session()

        # Set all SQL users inactive first - the ones still contained in the LDAP
        # will be set active again below (in the same transaction).
        for user in session.query(User):
            user.active = 0

        for plugin in self._ldap_plugins():
            ldap_userfolder = plugin._getLDAPUserFolder()

            ldap_util = ILDAPSearch(ldap_userfolder)
            ldap_users = ldap_util.get_users()

            for ldap_user in ldap_users:
                dn, info = ldap_user
                userid = info['userid']
                if not self.user_exists(userid):
                    # Create the new user
                    user = User(userid)
                    session.add(user)
                else:
                    # Get the existing user
                    user = session.query(User).filter_by(userid=userid).first()

                # Iterate over all SQL columns and update their values
                columns = User.__table__.columns
                for col in columns:
                    value = info.get(col.name)
                    setattr(user, col.name, value)

                # Set the user active
                user.active = 1
                print "Imported user '%s'..." % userid
            session.flush()

    def import_groups(self):
        """Imports groups from all the configured LDAP plugins into OGDS.
        """
        session = create_session()

        for plugin in self._ldap_plugins():
            ldap_userfolder = plugin._getLDAPUserFolder()

            ldap_util = ILDAPSearch(ldap_userfolder)
            ldap_groups = ldap_util.get_groups()

            for ldap_group in ldap_groups:
                dn, info = ldap_group

                # Group name is in the 'cn' attribute, which is mapped to 'fullname'
                info['groupid'] = info['fullname']
                groupid = info['groupid']
                if not self.group_exists(groupid):
                    # Create the new group
                    group = Group(groupid)
                    session.add(group)
                else:
                    # Get the existing group
                    group = session.query(Group).filter_by(groupid=groupid).first()

                # Iterate over all SQL columns and update their values
                columns = Group.__table__.columns
                for col in columns:
                    value = info.get(col.name)
                    setattr(group, col.name, value)

                members = info.get('uniqueMember', [])
                contained_users = []
                for user_dn in members:
                    try:
                        ldap_user = ldap_util.entry_by_dn(user_dn)
                        user_dn, user_info = ldap_user
                        if not 'userid' in user_info:
                            print "WARNING: User '%s' has no 'uid' attribute." % user_dn
                            continue
                        userid = user_info['userid']
                        user = self.get_sql_user(userid)
                        contained_users.append(user)
                        print "Importing user '%s'..." % userid
                    except NO_SUCH_OBJECT:
                        print "WARNING: Referenced user %s not found, ignoring!" % user_dn
                group.users = contained_users
                session.flush()
