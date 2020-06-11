from logging.handlers import TimedRotatingFileHandler
from opengever.base.model import create_session
from opengever.base.model import GROUP_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.pathfinder import PathFinder
from opengever.ogds.base.interfaces import ILDAPSearch
from opengever.ogds.base.interfaces import IOGDSSyncConfiguration
from opengever.ogds.base.interfaces import IOGDSUpdater
from opengever.ogds.base.sync.import_stamp import set_remote_import_stamp
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
from sqlalchemy import String
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from zope.component import adapter
from zope.interface import implementer
import logging
import os
import time


NO_UID_MSG = u"User {!r} has no 'uid' attribute."
NO_UID_AD_MSG = u"User {!r} has none of the attributes {!r} - skipping."
USER_NOT_FOUND_LDAP = u"Referenced user {!r} not found in LDAP, ignoring!"
USER_NOT_FOUND_SQL = u"Referenced user {!r} not found in SQL, ignoring!"

AD_UID_KEYS = [u'userid', u'sAMAccountName', u'windows_login_name']

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logger = logging.getLogger('opengever.ogds.base')
logger.setLevel(logging.INFO)


def sync_ogds(plone, users=True, groups=True):
    """Syncronize OGDS users and groups by importing users, groups and
    group membership information from LDAP into the respective OGDS SQL tables.

    If none of the `users` or `groups` keyword arguments are supplied, both
    users and groups will be imported. If one is set to false, only the other
    will be imported.

    NOTE: This function does *not* commit the transaction. Depending on from
    where you use it, you'll need to take care of that yourself, if necessary.
    """
    # Set up logging to a rotating ogds-update.log
    setup_ogds_sync_logfile(logger)

    updater = IOGDSUpdater(plone)
    start = time.clock()

    if users:
        logger.info(u"Importing users...")
        updater.import_users()

    if groups:
        logger.info(u"Importing groups...")
        updater.import_groups()

    elapsed = time.clock() - start
    logger.info(u"Done in {:0.1f} seconds.".format(elapsed))

    logger.info(u"Updating LDAP SYNC importstamp...")
    set_remote_import_stamp(plone)

    logger.info(u"Synchronization Done.")


def setup_ogds_sync_logfile(logger):
    """Sets up logging to a rotating var/log/ogds-update.log.
    """
    log_dir = PathFinder().var_log
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'ogds-update.log'),
        when='midnight', backupCount=7)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)


@implementer(IOGDSUpdater)
@adapter(IPloneSiteRoot)
class OGDSUpdater(object):
    """Adapter to synchronize users and groups from LDAP into OGDS.
    """

    def __init__(self, context):
        self.context = context

    def get_sql_user(self, userid):
        """Returns the OGDS user object identified by `userid`.
        """
        session = create_session()
        return session.query(User).filter_by(userid=userid).one()

    def get_sql_group(self, groupid):
        """Returns the OGDS group object identified by `groupid`.
        """
        session = create_session()
        return session.query(Group).filter_by(groupid=groupid).one()

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

    def _convert_value(self, value):
        """Joins multivalued (list or tuples) in to a single string and make
        sure its an unicode string.
        """
        # We can't store sequences in SQL columns. So if we do get
        # a multi-valued field to be stored directly in OGDS, we
        # treat it as a multi-line string and join it.
        if isinstance(value, list) or isinstance(value, tuple):
            return u' '.join([safe_unicode(v) for v in value])

        return safe_unicode(value)

    def get_group_title_ldap_attribute(self):
        return api.portal.get_registry_record(
            name='group_title_ldap_attribute',
            interface=IOGDSSyncConfiguration)

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
            logger.info(u'Users base: %s' % ldap_userfolder.users_base)
            logger.info(u'User filter: %s' % ldap_util.get_user_filter())

            ldap_users = ldap_util.get_users()

            for ldap_user in ldap_users:
                dn, info = ldap_user

                # Ignore users without an UID in LDAP
                if uid_attr not in info:
                    continue

                userid = info[uid_attr]
                userid = userid.decode('utf-8')

                # Skip users with uid longer than SQL 'userid' column
                if len(userid) > USER_ID_LENGTH:
                    logger.warn(u"Skipping user '{}' - "
                                u"userid too long!".format(userid))
                    continue

                if not self.user_exists(userid):
                    # Create the new user
                    user = User(userid)
                    session.add(user)
                else:
                    # Get the existing user
                    try:
                        user = self.get_sql_user(userid)
                    except MultipleResultsFound:
                        # Duplicate user with slightly different spelling
                        # (casing, whitespace, ...) that may not be considered
                        # different by the SQL backend's unique constraint.
                        # We therefore enforce uniqueness ourselves.
                        logger.warn(
                            u"Skipping duplicate user '{}'!".format(userid))
                        continue

                # Iterate over all SQL columns to be synchronized and update their values
                for col in user.columns_to_sync:
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

                    # Truncate purely descriptive user fields if necessary
                    if isinstance(col.type, String):
                        if value and len(value) > col.type.length:
                            logger.warn(
                                u"Truncating value %r for column %r "
                                u"(user: %r)" % (value, col.name, userid))
                            value = value[:col.type.length]

                    setattr(user, col.name, value)

                # Set the user active
                user.active = True
                logger.info(u"Imported user '{}'".format(userid))
            session.flush()

    def import_groups(self):
        """Imports groups from all the configured LDAP plugins into OGDS.
        """
        session = create_session()

        # Set all SQL groups inactive first - the ones still contained in the
        # LDAP will be set active again below (in the same transaction).
        #
        # Also set their `users` attribute to an empty collection in order
        # to clear out memberships from the `groups_users` association table
        # before importing them, so that memberships from groups that have
        # been deleted in LDAP get removed from OGDS.
        for group in session.query(Group):
            group.active = False
            group.users = []

        for plugin in self._ldap_plugins():
            ldap_userfolder = plugin._getLDAPUserFolder()

            ldap_util = ILDAPSearch(ldap_userfolder)
            logger.info(u'Groups base: %s' % ldap_userfolder.groups_base)
            logger.info(u'Group filter: %r' % ldap_util.get_group_filter())

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

                # Skip groups with groupid longer than SQL 'groupid' column
                if len(groupid) > GROUP_ID_LENGTH:
                    logger.warn(u"Skipping group '{}' - "
                                u"groupid too long!".format(groupid))
                    continue

                if not self.group_exists(groupid):
                    # Create the new group
                    group = Group(groupid)
                    session.add(group)
                else:
                    # Get the existing group
                    try:
                        group = self.get_sql_group(groupid)
                    except MultipleResultsFound:
                        # Duplicate group with slightly different spelling
                        # (casing, whitespace, ...) that may not be considered
                        # different by the SQL backend's unique constraint.
                        # We therefore enforce uniqueness ourselves.
                        logger.warn(
                            u"Skipping duplicate group '{}'!".format(groupid))
                        continue

                logger.info(u"Importing group '{}'...".format(groupid))

                # Iterate over all SQL columns to be synchronized and update their values
                for col in group.columns_to_sync:
                    setattr(group, col.name,
                            self._convert_value(info.get(col.name)))

                # Sync group title
                title_attribute = self.get_group_title_ldap_attribute()
                if title_attribute and info.get(title_attribute):
                    setattr(group, 'title',
                            self._convert_value(info.get(title_attribute)))

                contained_users = []
                group_members = ldap_util.get_group_members(info)

                for user_dn in group_members:
                    ldap_user = ldap_util.entry_by_dn(user_dn)

                    if ldap_user is None:
                        logger.warn(USER_NOT_FOUND_LDAP.format(user_dn))
                        continue

                    user_dn, user_info = ldap_user

                    if isinstance(user_dn, str):
                        user_dn = user_dn.decode('utf-8')

                    if not ldap_util.is_ad:
                        if 'userid' not in user_info:
                            logger.warn(NO_UID_MSG.format(user_dn))
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
                            logger.warn(NO_UID_AD_MSG.format(
                                user_dn, AD_UID_KEYS))
                            continue

                    if isinstance(userid, list):
                        userid = userid[0]

                    if isinstance(userid, str):
                        userid = userid.decode('utf-8')

                    try:
                        user = self.get_sql_user(userid)
                    except NoResultFound:
                        logger.warn(USER_NOT_FOUND_SQL.format(userid))
                        continue
                    except MultipleResultsFound:
                        # Duplicate user - skip (see above).
                        logger.warn(
                            u"  Skipping duplicate user '{}'!".format(userid))
                        continue

                    contained_users.append(user)
                    logger.info(
                        u"Importing user '{}' into group '{}'...".format(
                            userid, groupid))

                group.users = contained_users
                group.active = True
                session.flush()
                logger.info(u"Done.")
