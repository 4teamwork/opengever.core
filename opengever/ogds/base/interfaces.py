from zope import schema
from zope.interface import Interface


class IUser(Interface):
    """Marker interface for users.
    """


class IGroup(Interface):
    """Marker interface for groups.
    """


class IClient(Interface):
    """Marker interface for clients.
    """


class IGroup(Interface):
    """Marker interface for groups.
    """


class IClientConfiguration(Interface):
    """p.a.registry interface for configuring a client
    """

    client_id = schema.TextLine(
        title=u'Client ID',
        description=u'Enter the unique ID of this client. \
        It will be used by OGDS (Opengever Global Directory Service) \
        to identify this client.', )


class IContactInformation(Interface):
    """Contact information utility interface.
    """


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


class IObjectCreator(Interface):
    """ The object creator adapter creates a transported object.
    Discriminators: (FTI)
    Name: portal_type or ''
    Using the name "basedata" in the json-data dictionary
    """

    def extract(self):
        """ Extracts and returns the required data for object
        creation.
        This method must return a dictionary containing the portal_type.
        """

    def create(self, parent, data):
        """ Creates the object according to the data
        This method returns the created object
        """


class ISyncStamp(Interface):
    """Adapter Inteface for the Import Stamp"""


class IInternalOpengeverRequestLayer(Interface):
    """This request layer is activated on interal requests which are
    authenticated with the OGDS PAS plugin.
    """
