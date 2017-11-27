from __future__ import absolute_import
from five import grok
from ldap.controls import SimplePagedResultsControl
from opengever.ogds.base.interfaces import ILDAPSearch
from operator import itemgetter
from Products.LDAPMultiPlugins import ActiveDirectoryMultiPlugin
from Products.LDAPUserFolder.interfaces import ILDAPUserFolder
from Products.LDAPUserFolder.LDAPDelegate import filter_format
from Products.LDAPUserFolder.utils import GROUP_MEMBER_MAP
import ldap
import logging
import re


logger = logging.getLogger('opengever.ogds.base')

try:
    # python-ldap 2.4
    LDAP_CONTROL_PAGED_RESULTS = ldap.CONTROL_PAGEDRESULTS
    PYTHON_LDAP_24 = True
except AttributeError:
    # python-ldap 2.3
    LDAP_CONTROL_PAGED_RESULTS = ldap.LDAP_CONTROL_PAGE_OID
    PYTHON_LDAP_24 = False


ALL_OPERATIONAL_ATTRS = '1.3.6.1.4.1.4203.1.5.1'
KNOWN_MULTIVALUED_FIELDS = ['member', 'memberOf']
SUBSCHEMA_ATTRS = ['attributeTypes', 'dITContentRules', 'dITStructureRules',
                   'matchingRules', 'matchingRuleUse', 'nameForms',
                   'objectClasses']


class LDAPSearch(grok.Adapter):
    """Adapter to search LDAP for users and groups.

    Uses connection settings defined in the adapted LDAPUserFolder.
    """
    grok.provides(ILDAPSearch)
    grok.context(ILDAPUserFolder)

    def __init__(self, context):
        self.is_ad = False
        # context is a LDAPUserFolder instance
        self.context = context
        self._multivaluedness = {}
        self._supported_controls = None
        self._supported_features = None
        if isinstance(self.context.aq_parent, ActiveDirectoryMultiPlugin):
            self.is_ad = True
        self._cached_groups = None

    def connect(self):
        """Establish a connection (or return an existing one for re-use) by
        using the adapted LDAPUserFolder's _delegate.connect() method.

        This will use the LDAP server configuration and credentials defined
        for the adapted LDAPUserFolder.
        """
        ldap_uf = self.context
        self.base_dn = ldap_uf.users_base
        conn = ldap_uf._delegate.connect()
        return conn

    def _get_root_dse(self, conn=None):
        """Get the root DSE from the server.
        Returns a (root_dse_dn, root_dse_entry) tuple.
        """
        if conn is None:
            conn = self.connect()
        root_dse = conn.search_s('',
                                 ldap.SCOPE_BASE,
                                 '(objectclass=*)',
                                 ['*', '+'])[0]
        return root_dse

    @property
    def supported_controls(self):
        """Memoized access to controls supported by server.
        """
        if self._supported_controls is None:
            self._supported_controls = self._get_supported_controls()
        return self._supported_controls

    def _get_supported_controls(self):
        """Get supported server controls from root DSE.
        """
        conn = self.connect()
        root_dse_dn, root_dse_entry = self._get_root_dse(conn)

        supported_controls = root_dse_entry['supportedControl']
        return supported_controls

    @property
    def supported_features(self):
        """Memoized access to features supported by server.
        """
        if self._supported_features is None:
            self._supported_features = self._get_supported_features()
        return self._supported_features

    def _get_supported_features(self):
        """Get supported features from root DSE.
        """
        conn = self.connect()
        root_dse_dn, root_dse_entry = self._get_root_dse(conn)

        supported_features = root_dse_entry.get('supportedFeatures', [])
        return supported_features

    def get_schema(self):
        """Return the LDAP schema of the server we're currently connected to
        as an instance of ldap.schema.subentry.SubSchema.
        """

        if not hasattr(self, '_schema'):
            # Cache information about which attributes are multivalued.
            # This is schema dependent, so we initialize this cache the first
            # time we actually fetch the schema.
            self._multivaluedness = {}

            conn = self.connect()

            # Try to get schema DN from Root DSE
            root_dse_dn, root_dse_entry = self._get_root_dse(conn)

            try:
                schema_dn = root_dse_entry['subschemaSubentry'][0]
            except KeyError:
                schema_dn = 'cn=schema'

            attr_list = ['*', '+']
            if ALL_OPERATIONAL_ATTRS not in self.supported_features:
                # Server does not support RFC 3673 (returning all operational
                # attributes by using "+" in attribute list). We therefore
                # need to specify all known subschema attributes explicitely
                attr_list = SUBSCHEMA_ATTRS

            res = conn.search_s(schema_dn,
                                ldap.SCOPE_BASE,
                                '(objectclass=*)',
                                attr_list)

            if len(res) > 1:
                logger.warn("More than one LDAP schema found!")

            subschema_dn, subschema_subentry = res[0]
            self._schema = ldap.schema.subentry.SubSchema(subschema_subentry)

        return self._schema

    def _unpaged_search(self, base_dn, scope, search_filter, attrs):
        conn = self.connect()
        msgid = conn.search_ext(base_dn,
                                scope,
                                search_filter,
                                attrs,
                                serverctrls=[])
        rtype, rdata, rmsgid, serverctrls = conn.result3(msgid)
        results = rdata
        return results

    def _paged_search(self, base_dn, scope, search_filter, attrs):
        conn = self.connect()

        # Get paged results to prevent exceeding server size limit
        page_size = 1000
        if PYTHON_LDAP_24:
            lc = SimplePagedResultsControl(size=page_size, cookie='')
        else:
            lc = SimplePagedResultsControl(LDAP_CONTROL_PAGED_RESULTS,
                                           True,
                                           (page_size, ''),)
        is_last_page = False
        results = []

        while not is_last_page:
            msgid = conn.search_ext(base_dn,
                                    scope,
                                    search_filter,
                                    attrs,
                                    serverctrls=[lc])

            rtype, rdata, rmsgid, serverctrls = conn.result3(msgid)
            pctrls = [c for c in serverctrls
                      if c.controlType == LDAP_CONTROL_PAGED_RESULTS]

            results.extend(rdata)

            if pctrls:
                if PYTHON_LDAP_24:
                    cookie = pctrls[0].cookie
                    if cookie:
                        lc.cookie = cookie
                    else:
                        is_last_page = True
                else:
                    cookie = pctrls[0].controlValue[1]
                    if cookie:
                        # lc.controlValue seems to have been mutable at some
                        # point, now it's a tuple.
                        cv = list(lc.controlValue)
                        cv[1] = cookie
                        lc.controlValue = tuple(cv)
                    else:
                        is_last_page = True
            else:
                is_last_page = True
                logger.warn("Server ignores paged results control (RFC 2696).")

        return results

    def search(self, base_dn=None, scope=ldap.SCOPE_SUBTREE,
               search_filter='(objectClass=*)', attrs=[]):
        """Search LDAP for entries matching the given criteria, using result
        pagination if apprpriate, and return the results immediately.

        `base_dn`, `scope`, `search_filter` and `attrs` have the same meaning as the
        corresponding arguments on the ldap.search* methods.
        """

        if base_dn is None:
            base_dn = self.base_dn

        if LDAP_CONTROL_PAGED_RESULTS in self.supported_controls:
            try:
                results = self._paged_search(base_dn, scope, search_filter, attrs)

            except ldap.UNAVAILABLE_CRITICAL_EXTENSION:
                # Server does not support pagination controls - send search
                # request again without pagination controls
                results = self._unpaged_search(base_dn, scope, search_filter, attrs)
        else:
            results = self._unpaged_search(base_dn, scope, search_filter, attrs)

        # Skip result with None as first item, those are likely referral's,
        # we don't support those.
        results = filter(itemgetter(0), results)

        return results

    def get_users(self):
        """Return all LDAP users below the adapted LDAPUserFolder's
        users_base.

        If defined, the `user_filter` property on the adapted LDAPUserFolder
        is used to further filter the results.
        """
        # Get possible user object classes from adapted LDAPUserFolder
        user_object_classes = self.context._user_objclasses
        if len(user_object_classes) > 1:
            # If more than one possible user object class, OR them
            search_filter = '(|%s)' % ''.join(
                ['(objectClass=%s)' % oc for oc in user_object_classes])
        else:
            search_filter = '(objectClass=%s)' % user_object_classes[0]

        custom_filter = self.get_user_filter()
        if custom_filter:
            custom_filter = self._apply_schema_map_to_filter(custom_filter)
        search_filter = self._combine_filters(custom_filter, search_filter)

        mapped_results = []
        results = self.search(base_dn=self.context.users_base,
                              search_filter=search_filter)
        for result in results:
            mapped_results.append(self.apply_schema_map(result))

        return mapped_results

    def get_groups(self):
        """Return all LDAP groups below the adapted LDAPUserFolder's
        groups_base.

        If defined, the `group_filter` property on the adapted LDAPUserFolder
        is used to further filter the results.
        """
        # Build a filter expression that matches objectClasses for all
        # possible group objectClasseses encountered in the wild

        possible_classes = ''
        for oc in GROUP_MEMBER_MAP.keys():
            # concatenate (objectClass=foo) pairs
            possible_classes += filter_format('(%s=%s)', ('objectClass', oc))

        # Build the final OR expression:
        # (|(objectClass=aaa)(objectClass=bbb)(objectClass=ccc))
        search_filter = '(|%s)' % possible_classes

        custom_filter = self.get_group_filter()
        search_filter = self._combine_filters(custom_filter, search_filter)

        results = self.search(base_dn=self.context.groups_base,
                              search_filter=search_filter)

        mapped_results = []
        for result in results:
            mapped_results.append(self.apply_schema_map(result))

        return mapped_results

    def get_children(self, group_dn):
        children = []

        if self._cached_groups is None:
            self._cached_groups = self.get_groups()

        all_groups = self._cached_groups

        for grp_dn, grp_info in all_groups:
            parents = grp_info.get('memberOf', [])
            if group_dn in parents:
                # grp is a child group of group_dn
                children.append(grp_dn)
                # Recurse over grandchildren
                grandchildren = self.get_children(grp_dn)
                children.extend(grandchildren)
        return list(set(children))

    def get_group_members(self, group_info):
        if not self.is_ad:
            members = []
            member_attrs = list(set(GROUP_MEMBER_MAP.values()))
            for member_attr in member_attrs:
                if member_attr in group_info:
                    m = group_info.get(member_attr, [])
                    if isinstance(m, basestring):
                        m = [m]
                    members.extend(m)
            return members
        else:
            group_dn = group_info['distinguishedName']
            group_info['dn'] = group_dn

            if self._cached_groups is None:
                self._cached_groups = self.get_groups()

            child_groups = self.get_children(group_dn)
            child_groups.append(group_dn)

            members = []
            member_attrs = list(set(GROUP_MEMBER_MAP.values()))
            for grp_dn in child_groups:
                grp = [g for g in self._cached_groups if g[0] == grp_dn][0]
                for member_attr in member_attrs:
                    if member_attr in grp[1]:
                        m = grp[1].get(member_attr, [])
                        if isinstance(m, basestring):
                            m = [m]
                        members.extend(m)
            return list(set(members))

    def entry_by_dn(self, dn):
        """Retrieves an entry by its DN and applies the schema mapping to the
        attributes returned. Returns a (dn, attrs) tuple.

        Will raise ldap.NO_SUCH_OBJECT if the entry can't be found.
        """
        results = self.search(base_dn=dn, scope=ldap.SCOPE_BASE)

        # We query for a specific DN and therefor expect at most one entry
        entry = results[0]

        entry = self.apply_schema_map(entry)
        return entry

    def apply_schema_map(self, entry):
        """Apply the schema mapping configured in the adapted LDAPUserFolder
        to an entry.

        Expects a (dn, attrs) tuple and returns a copy of the tuple with keys
        in `attrs` renamed according to the mapping.
        """
        mapped_attrs = {}
        dn, attrs = entry

        # Check if entry is a user object - we only want to apply the
        # LDAPUserFolder mapping to those
        is_user = False
        obj_classes = attrs['objectClass']
        for obj_class in obj_classes:
            if obj_class.lower() in [uc.lower() for uc in
                                     self.context._user_objclasses]:
                is_user = True
                break

        # Get the list (!) of schema mapping dicts from LDAPUserFolder.
        schema_maps = self.context.getSchemaDict()
        mapped_attr_names = [attr['ldap_name'] for attr in schema_maps]

        # Deal with mapped attributes
        for schema_map in schema_maps:
            ldap_name = schema_map['ldap_name']
            public_name = schema_map['public_name']

            if ldap_name not in attrs:
                # Attribute not set (different from "present with None value")
                continue

            value = attrs[ldap_name]
            if isinstance(value, list) and not schema_map['multivalued']:
                value = value[0]

            if is_user:
                # Apply mapping
                mapped_attrs[public_name] = value
            else:
                # Otherwise leave key unchanged
                mapped_attrs[ldap_name] = value

        # Process remaining attributes
        for key in attrs:
            if key not in mapped_attr_names:
                if self._is_multivalued(attrs['objectClass'], key):
                    value = attrs[key]
                else:
                    value = attrs[key][0]
                mapped_attrs[key] = value

        return (dn, mapped_attrs)

    def get_user_filter(self):
        """Get the user filter expression defined for the adapted
        LDAPUserFolder by combining the GEVER custom property `user_filter`
        and the LDAPUserFolder's `_extra_user_filter`.
        """
        uf = self.context

        # TODO: Do we still need a custom property for this?
        user_filter = uf.getProperty('user_filter')

        extra_user_filter = uf.getProperty('_extra_user_filter')
        user_filter = self._combine_filters(user_filter, extra_user_filter)
        return user_filter

    def get_group_filter(self):
        """Get the group filter expression defined for the adapted
        LDAPUserFolder from the custom property `group_filter`.
        """
        uf = self.context
        return uf.getProperty('group_filter')

    def _apply_schema_map_to_filter(self, filterstr):
        """Rewrite attribute names in a LDAP filter expression according to the
        adapted LDAPUserFolder's schema mapping.
        """
        schema_maps = self.context.getSchemaDict()
        for schema_map in schema_maps:
            pattern = '\(%s([><~]?=)' % schema_map['public_name']
            repl = '(%s\\1' % schema_map['ldap_name']
            filterstr = re.sub(pattern, repl, filterstr)
        return filterstr

    def _combine_filters(self, filter_a, filter_b):
        """Combine two LDAP filter expressions with a boolean AND.

        If one of the filters is the empty string, simply return the other one.
        """
        if filter_a == '':
            return filter_b
        elif filter_b == '':
            return filter_a
        else:
            # Both filters are non-empty, need to combine them
            combined_filter = '(& %s %s)' % (filter_a, filter_b)
            return combined_filter

    def _get_object_classes(self):
        """Returns a list of tuples containing primary and alternative names
        for all objectClasses defined in the LDAP schema.
        """
        schema = self.get_schema()
        oc_tree = schema.tree(ldap.schema.ObjectClass)
        obj_classes = [schema.get_obj(ldap.schema.ObjectClass, oid) for
                       oid in oc_tree.keys()]
        obj_classes = [oc for oc in obj_classes if oc is not None]
        return obj_classes

    def _is_multivalued(self, obj_classes, attr_name):
        """Determine if an attribute is multivalued or not.
        First look in our internal cache, and in case of a miss, get the info
        from the schema and cache it.
        """
        if attr_name not in self._multivaluedness:
            self._multivaluedness[attr_name] = self._check_if_multivalued(
                obj_classes, attr_name)
        return self._multivaluedness[attr_name]

    def _check_if_multivalued(self, obj_classes, attr_name):
        """Given a list of object classes and the name of an attribute defined
        in one of those classes, use the LDAP schema to determine if the
        attribute is multi-valued or not.
        """
        schema = self.get_schema()
        try:
            attr_types = schema.attribute_types(obj_classes)
        except KeyError:
            # Broken schema, we need to guess
            if attr_name in KNOWN_MULTIVALUED_FIELDS:
                return True
            else:
                return False

        type_ = None
        found = False
        for type_map in attr_types:
            for attr_type in type_map.values():
                if attr_name in attr_type.names:
                    type_ = attr_type
                    found = True
                if found:
                    break
            if found:
                break

        if not found:
            logger.warn("Couldn't find attribute '%s' in schema for %s" %
                        (attr_name, obj_classes))
            return True

        return not type_.single_value
