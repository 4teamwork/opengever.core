from opengever.base.model import UNIT_ID_LENGTH
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface
import ldap


class IOGDSUpdater(Interface):
    """Adapter to synchronize users and groups from LDAP into OGDS.
    """

    def get_sql_user(userid):
        """Returns the OGDS user object identified by `userid`.
        """

    def user_exists(userid):
        """Checks whether the OGDS user identified by `userid` exists or not.
        """

    def group_exists(groupid):
        """Checks whether the OGDS group identified by `groupid` exists or not.
        """

    def import_users():
        """Imports users from all the configured LDAP plugins into OGDS.
        """

    def import_groups():
        """Imports groups from all the configured LDAP plugins into OGDS.
        """


class ILDAPSearch(Interface):
    """Interface describing an adapter to search LDAP for users and groups.

    Uses connection settings defined in the adapted LDAPUserFolder.
    """

    supported_controls = Attribute('List of controls supported by server.')

    def connect():
        """Establish a connection (or return an existing one for re-use) by
        using the adapted LDAPUserFolder's _delegate.connect() method.

        This will use the LDAP server configuration and credentials defined
        for the adapted LDAPUserFolder.
        """

    def get_schema():
        """Return the LDAP schema of the server we're currently connected to
        as an instance of ldap.schema.subentry.SubSchema.
        """

    def search(base_dn=None, scope=ldap.SCOPE_SUBTREE,
               filter='(objectClass=*)', attrs=[]):
        """Search LDAP for entries matching the given criteria, using result
        pagination if apprpriate, and return the results immediately.

        `base_dn`, `scope`, `filter` and `attrs` have the same meaning as the
        corresponding arguments on the ldap.search* methods.
        """

    def get_users():
        """Return all LDAP users below the adapted LDAPUserFolder's
        users_base.

        If defined, the `user_filter` property on the adapted LDAPUserFolder
        is used to further filter the results.
        """

    def get_groups():
        """Return all LDAP groups below the adapted LDAPUserFolder's
        groups_base.

        If defined, the `group_filter` property on the adapted LDAPUserFolder
        is used to further filter the results.
        """

    def entry_by_dn(dn):
        """Retrieves an entry by its DN and applies the schema mapping to the
        attributes returned. Returns a (dn, attrs) tuple.

        Will raise ldap.NO_SUCH_OBJECT if the entry can't be found.
        """

    def apply_schema_map(entry):
        """Apply the schema mapping configured in the adapted LDAPUserFolder
        to an entry.

        Expects a (dn, attrs) tuple and returns a copy of the tuple with keys in
        `attrs` renamed according to the mapping.
        """

    def get_user_filter():
        """Get the user filter expression defined for the adapted
        LDAPUserFolder from the custom property `user_filter`.
        """

    def get_group_filter():
        """Get the group filter expression defined for the adapted
        LDAPUserFolder from the custom property `group_filter`.
        """


class IAdminUnitConfiguration(Interface):

    current_unit_id = schema.TextLine(
        title=u'Id of the current Administrative Unit',
        description=u'The id of this administrative unit. It will be \
        mapped to the corresponding adminstrative unit configuration \
        in the OGDS (Opengever Global Directory Service).',
        max_length=UNIT_ID_LENGTH,
    )


class IOGDSSyncConfiguration(Interface):

    group_title_ldap_attribute = schema.TextLine(
        title=u'LDAP attribute name for the group title.',
        description=u'If attribute is not set, group title will not be synced.'
    )


class ISyncStamp(Interface):
    """Adapter Inteface for the Import Stamp"""


class IInternalOpengeverRequestLayer(Interface):
    """This request layer is activated on interal requests which are
    authenticated with the OGDS PAS plugin.
    """


class ITeam(Interface):
    """Marker interface for team object wrappers."""


class IUser(Interface):
    """Marker interface for user object wrappers."""
