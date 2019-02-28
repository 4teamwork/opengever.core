from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface, Attribute


class IOpengeverSharing(Interface):
    """Browserlayer Interface"""


# Events
class ILocalRolesAcquisitionBlocked(IObjectEvent):
    """Local Roles acquisition has been blocked"""


class ILocalRolesAcquisitionActivated(IObjectEvent):
    """Local Roles acquisition has been activated"""


class ILocalRolesModified(IObjectEvent):
    """Local Roles has been modified"""

    old_new_local_roles = Attribute("The local_roles before the modfication")
    new_local_roles = Attribute("The new local_roles after the modification")


# Registry Configuration
class ISharingConfiguration(Interface):
    """plone.app.registry interface for configuring the sharing view."""

    white_list_prefix = schema.TextLine(
        title=u'white list prefix',
        description=u'The prefix pattern for groups which should be displayed'
        'in the sharing view, even if the black list prefix also matches.',
        default=u"^.+")

    black_list_prefix = schema.TextLine(
        title=u'black list prefix',
        description=u"The prefix pattern for groups which shouldn't be "
        "displayed in the sharing view. For example another client group.",
        default=u"^$")


class IDisabledPermissionCheck(Interface):
    """Marker interface for disabled permisison check when fetching
    role_settings from the sharing view.
    """
