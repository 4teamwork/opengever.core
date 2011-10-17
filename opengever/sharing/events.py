from opengever.sharing.interfaces import ILocalRolesAcquisitionActivated
from opengever.sharing.interfaces import ILocalRolesAcquisitionBlocked
from opengever.sharing.interfaces import ILocalRolesModified
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class LocalRolesAcquisitionBlocked(ObjectEvent):
    """Local Roles acquisition has been blocked"""

    implements(ILocalRolesAcquisitionBlocked)


class LocalRolesAcquisitionActivated(ObjectEvent):
    """Local Roles acquisition has been activated"""

    implements(ILocalRolesAcquisitionActivated)


class LocalRolesModified(ObjectEvent):
    """Local Roles has been modified"""

    implements(ILocalRolesModified)

    def __init__(self, object, old_local_roles, new_local_roles):
        ObjectEvent.__init__(self, object)
        self.old_local_roles = old_local_roles
        self.new_local_roles = new_local_roles
