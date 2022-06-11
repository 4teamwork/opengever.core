from opengever.activity.model import query
from opengever.activity.model.activity import Activity
from opengever.activity.model.activity import ActivityTranslation
from opengever.activity.model.digest import Digest
from opengever.activity.model.notification import Notification
from opengever.activity.model.resource import Resource
from opengever.activity.model.resource import Subscription
from opengever.activity.model.settings import NotificationDefault
from opengever.activity.model.settings import NotificationSetting
from opengever.activity.model.watcher import Watcher


tables = [
    'activities',
    'activities_translation',
    'notifications',
    'resources',
    'watchers',
    'subscriptions',
    'notification_defaults',
    'notification_settings',
    'digests',
]
