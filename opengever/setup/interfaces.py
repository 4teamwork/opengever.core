from zope.interface import Interface


class IDeploymentConfigurationRegistry(Interface):
    """A deployment configuration registry is a utility which knows all the
    registered configurations.

    """
    def update_deployments(id, ident, attr):
        """Update or add a deployment configuration in the registry."""

    def get_deployment(ident):
        """Returns the deployment configuration (a dict) for the given
        identifier."""

    def list_deployments():
        """Returns a list of deployment titles."""


class ILDAPConfigurationRegistry(Interface):

    def update_ldaps(id, ident, attr):
        """Update or add a LDAP configuration in the registry."""

    def get_ldap(ident):
        """Returns the ldap configuration (a dict) for the given
        identifier."""

    def list_ldaps():
        """Returns a list of ldap titles."""
