from __future__ import absolute_import
from five import grok
from ldap.controls import SimplePagedResultsControl
from opengever.ogds.base.interfaces import ILDAPSearch
from Products.LDAPUserFolder.interfaces import ILDAPUserFolder
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


class LDAPSearch(grok.Adapter):
    """Adapter to search LDAP for users and groups.

    Uses connection settings defined in the adapted LDAPUserFolder.
    """
    grok.provides(ILDAPSearch)
    grok.context(ILDAPUserFolder)

    def __init__(self, context):
        # context is a LDAPUserFolder instance
        self.context = context

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

    def get_schema(self):
        """Return the LDAP schema of the server we're currently connected to
        as an instance of ldap.schema.subentry.SubSchema.
        """

        if not hasattr(self, '_schema'):
            conn = self.connect()

            # Try to get schema DN from Root DSE
            root_dse = conn.search_s('',
                                     ldap.SCOPE_BASE,
                                     '(objectclass=*)',
                                     ['*','+'])[0]

            root_dn, root_entry = root_dse

            try:
                schema_dn = root_entry['subschemaSubentry'][0]
            except KeyError:
                schema_dn = 'cn=schema'

            res = conn.search_s(schema_dn,
                                ldap.SCOPE_BASE,
                                '(objectclass=*)',
                                ['*','+'])

            if len(res) > 1:
                print "More than one LDAP schema found!"

            subschema_dn, subschema_subentry = res[0]
            self._schema = ldap.schema.subentry.SubSchema(subschema_subentry)

        return self._schema

    def search(self, base_dn=None, scope=ldap.SCOPE_SUBTREE,
               filter='(objectClass=*)', attrs=[]):
        """Search LDAP for entries matching the given criteria, using result
        pagination if apprpriate, and return the results immediately.

        `base_dn`, `scope`, `filter` and `attrs` have the same meaning as the
        corresponding arguments on the ldap.search* methods.
        """
        conn = self.connect()

        if base_dn is None:
            base_dn = self.base_dn

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
            try:
                msgid = conn.search_ext(base_dn,
                                        scope,
                                        filter,
                                        attrs,
                                        serverctrls=[lc])

                rtype, rdata, rmsgid, serverctrls = conn.result3(msgid)
                pctrls = [c for c in serverctrls
                          if c.controlType == LDAP_CONTROL_PAGED_RESULTS]

            except ldap.UNAVAILABLE_CRITICAL_EXTENSION:
                # Server does not support pagination controls - send search
                # request again without pagination controls
                msgid = conn.search_ext(base_dn,
                                        scope,
                                        filter,
                                        attrs,
                                        serverctrls=[])
                rtype, rdata, rmsgid, serverctrls = conn.result3(msgid)
                pctrls = []

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
                        # lc.controlValue seems to have been mutable at some point,
                        # now it's a tuple.
                        cv = list(lc.controlValue)
                        cv[1] = cookie
                        lc.controlValue = tuple(cv)
                    else:
                        is_last_page = True
            else:
                is_last_page = True
                logger.warn("Server ignores paged results control (RFC 2696).")
        return results

    def get_users(self):
        """Return all LDAP users below the adapted LDAPUserFolder's
        users_base.

        If defined, the `user_filter` property on the adapted LDAPUserFolder
        is used to further filter the results.
        """
        search_filter = '(objectClass=inetOrgPerson)'
        custom_filter = self.get_user_filter()
        if custom_filter not in [None, '']:
            custom_filter = self._apply_schema_map_to_filter(custom_filter)
            search_filter = self._combine_filters(custom_filter, search_filter)

        mapped_results = []
        results = self.search(base_dn=self.context.users_base,
                              filter=search_filter)
        for result in results:
            mapped_results.append(self.apply_schema_map(result))

        return mapped_results

    def get_groups(self):
        """Return all LDAP groups below the adapted LDAPUserFolder's
        groups_base.

        If defined, the `group_filter` property on the adapted LDAPUserFolder
        is used to further filter the results.
        """
        search_filter = '(objectClass=groupOfUniqueNames)'
        custom_filter = self.get_group_filter()
        if custom_filter not in [None, '']:
            custom_filter = self._apply_schema_map_to_filter(custom_filter)
            search_filter = self._combine_filters(custom_filter, search_filter)

        results = self.search(base_dn=self.context.groups_base,
                              filter=search_filter)
        mapped_results = []
        for result in results:
            mapped_results.append(self.apply_schema_map(result))

        return mapped_results

    def entry_by_dn(self, dn):
        """Retrieves an entry by its DN and applies the schema mapping to the
        attributes returned. Returns a (dn, attrs) tuple.

        Will raise ldap.NO_SUCH_OBJECT if the entry can't be found.
        """
        results = self.search(base_dn=dn, scope=ldap.SCOPE_BASE)
        return self.apply_schema_map(results[0])

    def apply_schema_map(self, entry):
        """Apply the schema mapping configured in the adapted LDAPUserFolder
        to an entry.

        Expects a (dn, attrs) tuple and returns a copy of the tuple with keys in
        `attrs` renamed according to the mapping.
        """
        mapped_attrs = {}
        dn, attrs = entry

        # Get the list (!) of schema mapping dicts from LDAPUserFolder.
        schema_maps = self.context.getSchemaDict()
        mapped_attr_names = [attr['ldap_name'] for attr in schema_maps]

        # Deal with mapped attributes
        for schema_map in schema_maps:
            ldap_name = schema_map['ldap_name']
            public_name = schema_map['public_name']

            if not ldap_name in attrs:
                # Attribute not set (different from "present with None value")
                continue

            value = attrs[ldap_name]
            if isinstance(value, list) and not schema_map['multivalued']:
                value = value[0]
            mapped_attrs[public_name] = value

        # Process remaining attributes
        for key in attrs:
            if not key in mapped_attr_names:
                if self._is_multivalued(attrs['objectClass'], key):
                    value = attrs[key]
                else:
                    value = attrs[key][0]
                mapped_attrs[key] = value

        return (dn, mapped_attrs)

    def get_user_filter(self):
        """Get the user filter expression defined for the adapted
        LDAPUserFolder from the custom property `user_filter`.
        """
        uf = self.context
        return uf.getProperty('user_filter')

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
        """
        combined_filter = '(& %s %s)' % (filter_a, filter_b)
        return combined_filter

    def _is_multivalued(self, obj_classes, attr_name):
        """Given a list of object classes and the name of an attribute defined
        in one of those classes, use the LDAP schema to determine if the
        attribute is multi-valued or not.
        """
        schema = self.get_schema()
        attr_types = schema.attribute_types(obj_classes)

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

