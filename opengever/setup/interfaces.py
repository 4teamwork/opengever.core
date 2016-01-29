from zope.interface import Interface


class IDeploymentConfigurationRegistry(Interface):
    """A deployment configuration registry is a utility which knows all the
    registered configurations.

    """
    def update_deployments(id, title, config_dict):
        """Update or add a deployment configuration in the registry.

        arguments:
          title: a string which is used as key
          config_dict: a dict containing deployment configuration options

        """

    def get_deployment(title):
        """Returns the deployment configuration (a dict) for the given
        identifier.

        """

    def list_deployments():
        """Returns a list of deployment titles."""


class ILDAPConfigurationRegistry(Interface):

    def update_ldaps(id, title, config_dict):
        """Update or add an LDAP configuration in the registry.

        arguments:
          title: a string which is used as key
          config_dict: a dict containing ldap configuration options

        """

    def get_ldap(title):
        """Returns the ldap configuration (a dict) for the given
        identifier.

        """

    def list_ldaps():
        """Returns a list of ldap titles."""
