from zope.interface import Interface, Attribute
from zope.component.interfaces import IObjectEvent


class IOpengeverSharing(Interface):
    """Browserlayer Interface"""


#Events
class ILocalRolesAcquisitionBlocked(IObjectEvent):
    """Local Roles acquisition has been blocked"""


class ILocalRolesAcquisitionActivated(IObjectEvent):
    """Local Roles acquisition has been activated"""


class ILocalRolesModified(IObjectEvent):
    """Local Roles has been modified"""

    old_new_local_roles = Attribute("The local_roles before the modfication")
    new_local_roles = Attribute("The new local_roles after the modification")
