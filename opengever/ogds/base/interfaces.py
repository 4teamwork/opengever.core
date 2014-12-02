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
        in the OGDS (Opengever Global Directory Service).', )


class IClientCommunicator(Interface):
    """Utility interface for the client communicator.
    """


class ITransporter(Interface):
    """Utility interface for the transporter utility, which
    is able to copy objects between tentacles (clients).
    """


class IDataCollector(Interface):
    """ Interface for adapters which are able to serialize and
    unserialize data. With these named-adapters any kind of additional
    information can be transmitted.
    Discriminators: object
    Name: unique adapter name, which is used as key for sending the data
    """

    def extract(self):
        """ Returns the serialized data. Serialized data consists of raw
        type data (dicts, lists, tuples, strings, numbers, bools, etc. ).
        The data is json-able.
        """

    def insert(self, data):
        """ Unserializes the *data* and changes the *obj* according to the
        data.
        """


class ISyncStamp(Interface):
    """Adapter Inteface for the Import Stamp"""


class IInternalOpengeverRequestLayer(Interface):
    """This request layer is activated on interal requests which are
    authenticated with the OGDS PAS plugin.
    """
