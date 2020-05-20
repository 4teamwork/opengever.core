from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface


class INotificationEvent(IObjectEvent):

    kind = Attribute("The kind of the activity")
    summary = Attribute("The title of the activity")
    actor = Attribute("The actor which performed the activity")
    description = Attribute("The description of the activity")


class IWatcherAddedEvent(IObjectEvent):

    oguid = Attribute("The oguid of the object to which a watcher is added")
    watcherid = Attribute("The userid of the added watcher")


class IActivitySettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable activity feature',
        description=u'Whether features from opengever.activity are enabled',
        default=True)
