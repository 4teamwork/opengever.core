from App.config import getConfiguration
from five import grok
from ldap import NO_SUCH_OBJECT
from opengever.core.model import create_session
from opengever.ogds.base.interfaces import ILDAPSearch
from opengever.ogds.base.interfaces import IOGDSUpdater
from opengever.ogds.base.sync.import_stamp import set_remote_import_stamp
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
import logging
import time


NO_UID_MSG = "User '%s' has no 'uid' attribute."
NO_UID_AD_MSG = "User '%s' has none of the attributes %s - skipping."
USER_NOT_FOUND_LDAP = "Referenced user %s not found in LDAP, ignoring!"
USER_NOT_FOUND_SQL = "Referenced user %s not found in SQL, ignoring!"

AD_UID_KEYS = ['userid', 'sAMAccountName', 'windows_login_name']

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logger = logging.getLogger('opengever.ogds.base')


def sync_ogds(plone, users=True, groups=True):
    """Syncronize OGDS users and groups by importing users, groups and
    group membership information from LDAP into the respective OGDS SQL tables.

    If none of the `users` or `groups` keyword arguments are supplied, both
    users and groups will be imported. If one is set to false, only the other
    will be imported.

    NOTE: This function does *not* commit the transaction. Depending on from
    where you use it, you'll need to take care of that yourself, if necessary.
    """

    # Set up log handler for logging to ogds_log_file
    config = getConfiguration()
    ogds_conf = config.product_config.get('opengever.core', dict())
    log_file = ogds_conf.get('ogds_log_file')

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

    updater = IOGDSUpdater(plone)
    start = time.clock()

    if users:
        logger.info("Importing users...")
        updater.import_users()

    if groups:
        logger.info("Importing groups...")
        updater.import_groups()

    elapsed = time.clock() - start
    logger.info("Done in %.0f seconds." % elapsed)

    logger.info("Updating LDAP SYNC importstamp...")
    set_remote_import_stamp(plone)

    logger.info("Synchronization Done.")


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

    def _get_uid_attr(self, ldap_userfolder):
        """Returns the UID attribute from the given LDAPUserFolder. If that
        attribute is mapped, the mapped public name will be returned.
        """
        uid_attr = ldap_userfolder._uid_attr
        schema_dicts = ldap_userfolder.getSchemaDict()
        for schema_map in schema_dicts:
            if uid_attr == schema_map['ldap_name']:
                return schema_map['public_name']
        return uid_attr

    def import_users(self):
        """Imports users from all the configured LDAP plugins into OGDS.
        """
        session = create_session()

        # Set all SQL users inactive first - the ones still contained in the
        # LDAP will be set active again below (in the same transaction).
        for user in session.query(User):
            user.active = False

        for plugin in self._ldap_plugins():
            ldap_userfolder = plugin._getLDAPUserFolder()
            uid_attr = self._get_uid_attr(ldap_userfolder)

            ldap_util = ILDAPSearch(ldap_userfolder)
            ldap_users = ldap_util.get_users()

            for ldap_user in ldap_users:
                dn, info = ldap_user

                # Ignore users without an UID in LDAP
                if not uid_attr in info:
                    continue

                userid = info[uid_attr]
                userid = userid.decode('utf-8')

                # Skip users with uid longer than SQL 'userid' column
                # FIXME: Increase size of SQL column to 64
                if len(userid) > 30:
                    continue

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
                    if col.name == 'userid':
                        # We already set the userid when creating the user
                        # object, and it may not be called the same in LDAP as
                        # in our SQL model
                        continue
                    value = info.get(col.name)

                    # We can't store sequences in SQL columns. So if we do get
                    # a multi-valued field to be stored directly in OGDS, we
                    # treat it as a multi-line string and join it.
                    if isinstance(value, list) or isinstance(value, tuple):
                        value = ' '.join([str(v) for v in value])

                    if isinstance(value, str):
                        value = value.decode('utf-8')

                    setattr(user, col.name, value)

                # Set the user active
                user.active = True
                logger.info("Imported user '%s'" % userid)
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

                # Group name is in the 'cn' attribute, which may be
                # mapped to 'fullname'
                if 'cn' in info:
                    groupid = info['cn']
                    if isinstance(groupid, list):
                        groupid = groupid[0]
                else:
                    groupid = info['fullname']

                groupid = groupid.decode('utf-8')
                info['groupid'] = groupid

                if not self.group_exists(groupid):
                    # Create the new group
                    group = Group(groupid)
                    session.add(group)
                else:
                    # Get the existing group
                    group = session.query(Group).filter_by(
                        groupid=groupid).first()

                # Iterate over all SQL columns and update their values
                columns = Group.__table__.columns
                for col in columns:
                    value = info.get(col.name)

                    # We can't store sequences in SQL columns. So if we do get
                    # a multi-valued field to be stored directly in OGDS, we
                    # treat it as a multi-line string and join it.
                    if isinstance(value, list) or isinstance(value, tuple):
                        value = ' '.join([str(v) for v in value])

                    if isinstance(value, str):
                        value = value.decode('utf-8')

                    setattr(group, col.name, value)

                contained_users = []
                group_members = ldap_util.get_group_members(info)

                logger.info("Importing group '%s'..." % groupid)
                for user_dn in group_members:
                    try:
                        ldap_user = ldap_util.entry_by_dn(user_dn)
                        user_dn, user_info = ldap_user

                        if isinstance(user_dn, str):
                            user_dn = user_dn.decode('utf-8')

                        if not ldap_util.is_ad:
                            if not 'userid' in user_info:
                                logger.warn(NO_UID_MSG % user_dn)
                                continue
                            userid = user_info['userid']
                        else:
                            # Active Directory
                            uid_found = False
                            for uid_key in AD_UID_KEYS:
                                if uid_key in user_info:
                                    userid = user_info[uid_key]
                                    uid_found = True
                                    break
                            if not uid_found:
                                # No suitable UID found, skip this user
                                logger.warn(NO_UID_AD_MSG % (user_dn,
                                                             AD_UID_KEYS))
                                continue

                        if isinstance(userid, list):
                            userid = userid[0]

                        if isinstance(userid, str):
                            userid = userid.decode('utf-8')

                        user = self.get_sql_user(userid)
                        if user is None:
                            logger.warn(USER_NOT_FOUND_SQL % userid)
                            continue

                        contained_users.append(user)
                        logger.info("Importing user '%s' "
                                    "into group '%s'..." % (userid, groupid))
                    except NO_SUCH_OBJECT:
                        logger.warn(USER_NOT_FOUND_LDAP % user_dn)
                group.users = contained_users
                session.flush()
                logger.info("Done.")
