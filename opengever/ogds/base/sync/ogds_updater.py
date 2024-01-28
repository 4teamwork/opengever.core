from logging.handlers import TimedRotatingFileHandler
from opengever.base.exceptions import IncorrectConfigurationError
from opengever.base.model import create_session
from opengever.base.model import GROUP_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.pathfinder import PathFinder
from opengever.base.sentry import maybe_report_exception
from opengever.base.utils import check_group_plugin_configuration
from opengever.ogds.base.interfaces import ILDAPSearch
from opengever.ogds.base.interfaces import IOGDSSyncConfiguration
from opengever.ogds.base.interfaces import IOGDSUpdater
from opengever.ogds.base.sync.import_stamp import set_remote_import_stamp
from opengever.ogds.base.sync.sid2str import sid2str
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
from sqlalchemy import String
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.expression import true
from UserDict import UserDict
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import implementer
import logging
import os
import requests
import time


class CaseInsensitiveDict(UserDict):
    """Dictionary class that supports case insensitive lookups.

    NOTE: This is only intended for use the OGDSUpdater below. It is not fit
    for purpose as a generic case insensitive dict, so please resist the
    temptation to move this into some utils.py and reuse it without checking.

    This dictionary has the following properties:
    - The following operations are case-insensitive:
      - dct.get(key)
      - dct[key]
      - key in dct
    - The two lookup methods will always prioritize an exact case match, if
      the dict should contain two "duplicate" keys that only differ in case.
    - Case of keys is preserved, so dct.keys() returns the original spelling.
    """

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        for k, v in self.data.items():
            if k.lower() == key.lower():
                return v
        raise KeyError(key)

    def get(self, key, failobj=None):
        if key in self.data:
            return self[key]
        for k, v in self.data.items():
            if k.lower() == key.lower():
                return v
        return failobj

    def __contains__(self, key):
        if key in self.data:
            return True
        for k in self.data:
            if k.lower() == key.lower():
                return True
        return False


IGNORED_LOCAL_GROUPS = set([
    'Administrators', 'Site Administrators', 'Reviewers'])

NO_UID_MSG = u"User {!r} has no 'uid' attribute."
NO_UID_AD_MSG = u"User {!r} has none of the attributes {!r} - skipping."
USER_NOT_FOUND_LDAP = u"Referenced user {!r} not found in LDAP, ignoring!"

AD_UID_KEYS = [u'userid', u'sAMAccountName', u'windows_login_name']

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logger = logging.getLogger('opengever.ogds.base')
logger.setLevel(logging.INFO)


def sync_ogds(plone, users=True, groups=True, local_groups=False,
              update_remote_timestamps=True, disable_logfile=False):
    """Syncronize OGDS users and groups by importing users, groups and
    group membership information from LDAP into the respective OGDS SQL tables.

    If none of the `users` or `groups` keyword arguments are supplied, both
    users and groups will be imported. If one is set to false, only the other
    will be imported.

    NOTE: This function does *not* commit the transaction. Depending on from
    where you use it, you'll need to take care of that yourself, if necessary.
    """
    # Set up logging to a rotating ogds-update.log
    if not disable_logfile:
        try:
            setup_ogds_sync_logfile(logger)
        except RuntimeError:
            # in some cases (testserver and other test builds), the specific
            # logger cannot be setupped. We can ignore this case and use the
            # default logfile
            pass

    # We check that the group management is setup correctly. This is not
    # strictly necessary but ensures that this configuration is checked
    # on a regular basis and that the @groups endpoint is safe.
    check_group_manager(plone)

    updater = IOGDSUpdater(plone)
    start = time.time()

    if users:
        logger.info(u"Importing users...")
        updater.import_users()

    if groups:
        logger.info(u"Importing groups...")
        updater.import_groups()

    if local_groups:
        logger.info(u"Importing local groups...")
        updater.import_local_groups()

    elapsed = time.time() - start
    logger.info(u"Done in {:0.1f} seconds.".format(elapsed))

    if update_remote_timestamps:
        logger.info(u"Updating LDAP SYNC importstamp...")
        set_remote_import_stamp(plone)

    logger.info(u"Synchronization Done.")


def setup_ogds_sync_logfile(logger):
    """Sets up logging to a rotating var/log/ogds-update.log.
    """
    handler_name = "ogds_update"
    for handler in logger.handlers:
        if isinstance(handler, TimedRotatingFileHandler) and handler.get_name() == handler_name:
            return
    log_dir = PathFinder().var_log
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'ogds-update.log'),
        when='midnight', backupCount=7)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    file_handler.set_name(handler_name)
    logger.addHandler(file_handler)


def check_group_manager(context):
    """We make sure here that the site is setup correctly in that @groups
    will write to source_groups and not to the ldap and that enumeration
    is enabled for the source_groups plugin. This is especially important
    for Teamraum deployments where the @groups endpoint is actually used.
    """
    try:
        check_group_plugin_configuration(context)
    except IncorrectConfigurationError as exc:
        maybe_report_exception(
            context, getRequest(), exc.__class__.__name__, exc.message)


@implementer(IOGDSUpdater)
@adapter(IPloneSiteRoot)
class OGDSUpdater(object):
    """Adapter to synchronize users and groups from LDAP into OGDS.
    """

    def __init__(self, context):
        self.context = context
        self.ogds_sync_url = os.environ.get('OGDS_SYNC_URL', '').rstrip('/')

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
        if self.ogds_sync_url:
            try:
                resp = requests.post(self.ogds_sync_url + '/sync-users')
                resp.raise_for_status()
            except requests.exceptions.RequestException:
                logger.exception('Syncing users failed.')
            else:
                logger.info(resp.text)
            return

        session = create_session()

        ldap_users = self.ldap_users()
        ogds_users = {
            user.userid: {
                col: getattr(user, col)
                for col in user.column_names_to_sync
            } for user in session.query(User)
        }

        added_mappings, deleted_mappings, modified_mappings = self.update_mappings(
            ldap_users, ogds_users)

        session.bulk_insert_mappings(User, added_mappings)
        for added in added_mappings:
            logger.info('Added user %s', added['userid'])

        session.bulk_update_mappings(User, deleted_mappings + modified_mappings)
        for deleted in deleted_mappings:
            logger.info('Deactivated user %s', deleted['userid'])
        for modified in modified_mappings:
            logger.info('Modified user %s', modified['userid'])

        logger.info('Users added: %s', len(added_mappings))
        logger.info('Users deactivated: %s', len(deleted_mappings))
        logger.info('Users modified: %s', len(modified_mappings))

    def import_groups(self):
        """Imports groups from all the configured LDAP plugins into OGDS.
        """
        if self.ogds_sync_url:
            try:
                resp = requests.post(self.ogds_sync_url + '/sync-groups')
                resp.raise_for_status()
            except requests.exceptions.RequestException:
                logger.exception('Syncing groups failed.')
            else:
                logger.info(resp.text)
            return

        session = create_session()

        ldap_groups, ldap_group_members = self.ldap_groups_and_members()
        ogds_groups = {}
        ogds_group_members = {}
        for group in (
            session.query(Group)
            .filter(or_(Group.is_local.is_(None), Group.is_local == false()))
        ):
            ogds_groups[group.groupid] = {
                col: getattr(group, col)
                for col in group.column_names_to_sync
            }
            ogds_group_members[group.groupid] = set(
                [user.userid for user in group.users])

        # Ignore local OGDS groups
        local_ogds_groups = set([
            group.groupid for group
            in session.query(Group).filter(Group.is_local == true())
        ])
        for local_group in local_ogds_groups:
            if local_group in ldap_groups:
                del ldap_groups[local_group]
            if local_group in ldap_group_members:
                del ldap_group_members[local_group]

        added_mappings, deleted_mappings, modified_mappings = self.update_mappings(
            ldap_groups, ogds_groups, pk='groupid')

        session.bulk_insert_mappings(Group, added_mappings)
        for added in added_mappings:
            logger.info('Added group %s', added['groupid'])

        session.bulk_update_mappings(Group, deleted_mappings + modified_mappings)
        for deleted in deleted_mappings:
            logger.info('Deactivated group %s', deleted['groupid'])
        for modified in modified_mappings:
            logger.info('Modified group %s', modified['groupid'])

        # Update group members
        ogds_users = {
            user.userid: user for user in session.query(User)
        }

        ogds_user_ids_ci = CaseInsensitiveDict(
            zip(ogds_users.keys(), ogds_users.keys()))

        ogds_groups = {
            group.groupid: group
            for group in session.query(Group).filter(
                or_(Group.is_local.is_(None), Group.is_local == false())
            )
        }

        modified_count = 0
        for groupid in ldap_group_members.keys():
            diff = ldap_group_members[groupid] ^ ogds_group_members.get(groupid, set())
            if diff:
                group = ogds_groups[groupid]

                # Case insensitive lookup of existing OGDS user via userid
                # from LDAP (which may differ in capitalization).
                group.users = [
                    ogds_users[ogds_user_ids_ci[userid]] for userid
                    in ldap_group_members[groupid]
                ]

                for userid in diff:
                    if userid in ogds_group_members.get(groupid, set()):
                        logger.info('Removed user %s from group %s.', userid, groupid)
                    else:
                        logger.info('Added user %s into group %s.', userid, groupid)
                modified_count += 1

        for deleted in deleted_mappings:
            group = ogds_groups[deleted['groupid']]
            group.users = []
            logger.info('Removed all users from group %s.', deleted['groupid'])
            modified_count += 1

        logger.info('Groups added: %s', len(added_mappings))
        logger.info('Groups deactivated: %s', len(deleted_mappings))
        logger.info('Groups modified: %s', len(modified_mappings))
        logger.info('Groups with modified membership: %s', modified_count)
        session.flush()

    def import_local_groups(self):
        session = create_session()

        local_groups, local_group_members = self.plone_groups()
        ogds_groups = {}
        ogds_group_members = {}
        for group in (session.query(Group).filter(Group.is_local == true())):
            ogds_groups[group.groupid] = {
                col: getattr(group, col)
                for col in group.column_names_to_sync ^ set(['is_local'])
            }
            ogds_group_members[group.groupid] = set(
                [user.userid for user in group.users])

        # Ignore global OGDS groups
        global_ogds_groups = set([
            group.groupid for group
            in session.query(Group).filter(
                or_(Group.is_local.is_(None), Group.is_local == false())
            )
        ])
        for global_group in global_ogds_groups:
            if global_group in local_groups:
                del local_groups[global_group]
            if global_group in local_group_members:
                del local_group_members[global_group]

        added_mappings, deleted_mappings, modified_mappings = self.update_mappings(
            local_groups, ogds_groups, pk='groupid')

        session.bulk_insert_mappings(Group, added_mappings)
        for added in added_mappings:
            logger.info('Added local group %s', added['groupid'])

        session.bulk_update_mappings(Group, deleted_mappings + modified_mappings)
        for deleted in deleted_mappings:
            logger.info('Deactivated local group %s', deleted['groupid'])
        for modified in modified_mappings:
            logger.info('Modified local group %s', modified['groupid'])

        # Update group members
        ogds_users = {
            user.userid: user for user in session.query(User)
        }
        ogds_groups = {
            group.groupid: group
            for group in session.query(Group).filter(Group.is_local == true())
        }

        modified_count = 0
        for groupid in local_group_members.keys():
            local_ogds_group_members = set([
                m for m in local_group_members[groupid] if m in ogds_users])
            diff = local_ogds_group_members ^ ogds_group_members.get(groupid, set())
            if diff:
                group = ogds_groups[groupid]
                group.users = [
                    ogds_users[userid] for userid
                    in local_ogds_group_members
                ]
                for userid in local_group_members[groupid]:
                    logger.info('Added user %s into local group %s.', userid, groupid)
                modified_count += 1

        logger.info('Local groups added: %s', len(added_mappings))
        logger.info('Local groups deactivated: %s', len(deleted_mappings))
        logger.info('Local groups modified: %s', len(modified_mappings))
        logger.info('Local groups with modified membership: %s', modified_count)
        session.flush()

    def ldap_users(self):
        """Fetch users from LDAP"""
        users = {}

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

                user_attrs = {}
                for col in User.columns_to_sync:
                    value = info.get(col.name)

                    # We can't store sequences in SQL columns. So if we do get
                    # a multi-valued field to be stored directly in OGDS, we
                    # treat it as a multi-line string and join it.
                    if isinstance(value, (list, tuple)):
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

                    user_attrs[col.name] = value

                user_attrs['active'] = True
                user_attrs['external_id'] = userid
                user_attrs['username'] = userid

                object_sid = info.get('objectSid')
                if object_sid:
                    user_attrs['object_sid'] = sid2str(object_sid)

                # The LDAP/AD attributes 'displayName' or 'cn' are sometimes
                # mapped to the 'fullname' property. If it exists, we store
                # this in OGDS in the display_name column.
                # This is therefore a customer-controlled display name, and
                # different from the full name we build in the User.fullname()
                # method by concatenating first and last name.
                display_name = info.get('fullname')
                if display_name:
                    user_attrs['display_name'] = display_name.decode('utf-8')

                users[userid] = user_attrs

        return users

    def ldap_groups_and_members(self):
        """Fetch groups and group members from LDAP"""
        groups = {}
        members = {}
        for plugin in self._ldap_plugins():
            ldap_userfolder = plugin._getLDAPUserFolder()

            ldap_util = ILDAPSearch(ldap_userfolder)
            logger.info(u'Groups base: %s' % ldap_userfolder.groups_base)
            logger.info(u'Group filter: %r' % ldap_util.get_group_filter())

            ldap_groups = ldap_util.get_groups()
            ldap_users = {dn.lower(): info for dn, info in ldap_util.get_users()}

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
                try:
                    groupid.encode('ascii')
                except UnicodeEncodeError:
                    logger.warn(
                        u"Skipping group '{}' - contains non-ascii characters".format(groupid))
                    continue
                info['groupid'] = groupid

                # Skip groups with groupid longer than SQL 'groupid' column
                if len(groupid) > GROUP_ID_LENGTH:
                    logger.warn(u"Skipping group '{}' - "
                                u"groupid too long!".format(groupid))
                    continue

                group_attrs = {}
                for col in Group.columns_to_sync:
                    group_attrs[col.name] = self._convert_value(
                        info.get(col.name))
                title_attribute = self.get_group_title_ldap_attribute()
                if title_attribute and info.get(title_attribute):
                    group_attrs['title'] = self._convert_value(
                        info.get(title_attribute))
                group_attrs['active'] = True
                group_attrs['external_id'] = groupid
                group_attrs['groupname'] = groupid
                groups[groupid] = group_attrs

                contained_users = set()
                group_members = ldap_util.get_group_members(info)

                for user_dn in group_members:
                    user_info = ldap_users.get(user_dn.lower())

                    if user_info is None:
                        logger.warn(USER_NOT_FOUND_LDAP.format(user_dn))
                        continue

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

                    contained_users.add(userid)

                members[groupid] = contained_users

        return groups, members

    def plone_groups(self):
        """Returns local Plone groups"""
        uf = getToolByName(self.context, 'acl_users')
        groups_plugin = uf.plugins.get('source_groups')

        groups = {}
        members = {}
        for group in groups_plugin.getGroups():
            groupid = group.getId()
            if groupid in IGNORED_LOCAL_GROUPS:
                continue
            title = groups_plugin.getGroupInfo(groupid).get('title')
            if title is not None:
                title = safe_unicode(title)
            groups[groupid] = {
                'groupid': groupid.decode('utf8'),
                'groupname': groupid.decode('utf8'),
                'external_id': groupid.decode('utf8'),
                'title': title,
                'active': True,
                'is_local': True,
            }
            members[groupid] = group.getMemberIds()
        return groups, members

    def update_mappings(self, ldap_objects, ogds_objects, pk='userid'):
        """Determine difference between LDAP and OGDS objects and return
           mappings for bulk inserts/updates.
        """
        ldap_keys = set(ldap_objects.keys())
        ogds_keys = set(ogds_objects.keys())

        ldap_objects_ci = CaseInsensitiveDict(ldap_objects)
        ogds_objects_ci = CaseInsensitiveDict(ogds_objects)

        ogds_active_keys = set(
            [key for key, value in ogds_objects.items() if value.get('active')])

        added = ldap_keys - ogds_keys

        # Don't add users with different capitalization in LDAP than an
        # existing OGDS user as new, duplicate users in OGDS that would only
        # differ in case.
        #
        # We still consider them for updating properties and group memberships
        # of the existing OGDS user though.
        added_ci = set([
            userid for userid in added
            if userid not in ogds_objects_ci])

        for skipped in added - added_ci:
            logger.info('Not adding duplicate user with deviating case {}'.format(skipped))

        deleted = [k for k in ogds_active_keys if k not in ldap_objects_ci]
        existing = [k for k in ogds_keys if k in ldap_objects_ci]
        modified = {}
        for key in existing:
            # Case-insensitive lookup of the matching LDAP record
            ldap_record = ldap_objects_ci[key]
            ogds_record = ogds_objects[key]

            diff = set(ldap_record.items()) ^ set(ogds_record.items())
            if diff:
                attributes = dict(diff).keys()
                # Never modify an existing userid or external_id in OGDS.
                # They may differ in case if userid was changed in LDAP/AD.
                attributes = filter(
                    lambda x: x not in ['userid', 'external_id'], attributes)
                if attributes:
                    modified[key] = attributes

        added_mappings = [ldap_objects[a] for a in added_ci]
        deleted_mappings = [{pk: d, 'active': False} for d in deleted]
        modified_mappings = []
        for key, modified_attrs in modified.items():
            changes = {pk: key}
            # Case-insensitive lookup of the matching LDAP record
            ldap_record = ldap_objects_ci[key]
            for modified_attr in modified_attrs:
                changes[modified_attr] = ldap_record[modified_attr]
            modified_mappings.append(changes)

        return added_mappings, deleted_mappings, modified_mappings
