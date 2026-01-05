from Products.PlonePAS.interfaces.propertysheets import IMutablePropertySheet
from Products.PluggableAuthService.UserPropertySheet import UserPropertySheet
from zope.interface import implements


class OGDSAuthPropertySheet(UserPropertySheet):
    """This property sheet is used by the OGDS Auth Plugin to prevent
    writing of user properties but still provide a mutable property sheet.

    The logic for updating ogds properties should be implemented in this
    property sheet but is currently implemented directly in the api endpoints.
    We won't do any refactoring now and just provide a no-op implementation to
    avoid errors when PlonePAS tries to update user properties.

    The OGDS-Auth plugin provides a PropertiesPlugin which will be used to
    read user properties from the OGDS. The plugin is not meant to write any
    properties back to the OGDS but the PlonePAS framework expects the property
    sheets to provide a mutable property sheet anyway.

    Fixes https://4teamwork.atlassian.net/browse/TI-3525
    """
    implements(IMutablePropertySheet)

    def canWriteProperty(self, object, id):
        return False

    def setProperty(self, object, id, value):
        pass

    def setProperties(self, object, mapping):
        pass
