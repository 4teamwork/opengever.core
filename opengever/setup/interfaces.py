from zope.interface import Interface


class IClientConfigurationRegistry(Interface):
    """A client configuration registry is a utility which.
    Knows all the registered configurations."""

    def update_clients(id, attr):
        """Update or add client configuration to the
        client-configuration registry."""

    def update_policy(id, attr):
        """Update or add policy to the client-configuration registry."""

    def get_configuration(id):
        """Returns the client configuration (a dict) for the given id. """

    def get_policy(id):
        """Returns a dict with all policy attributes. Include a list
        of client configurations on the key `clients`.

        For policies with the multiclient option, it appends ten generated
        clients, and fill in the client_number if it's necessary."""

    def get_policies():
        """Returns a generator wiht all registered policy configurations."""

    def list_policies():
        """Returns a list policy titles."""
