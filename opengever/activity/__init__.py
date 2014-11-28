from opengever.activity.models.activity import Activity
from opengever.activity.models.notification import Notification
from opengever.activity.models.resource import Resource
from opengever.activity.models.watcher import Watcher
from z3c.saconfig import named_scoped_session
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("opengever.activity")

Session = named_scoped_session("opengever")
