from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute


class INotificationEvent(IObjectEvent):

    kind = Attribute("The kind of the activity")
    title = Attribute("The title of the activity")
    actor = Attribute("The user object, which did the activity")
    description = Attribute("The description of the activity")
