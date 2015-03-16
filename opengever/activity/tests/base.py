from opengever.activity.models.activity import Activity
from opengever.activity.models.notification import Notification
from opengever.activity.models.resource import Resource
from opengever.activity.models.watcher import Watcher
from opengever.testing import MEMORY_DB_LAYER
import unittest2



class ActivityTestCase(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    @property
    def session(self):
        return self.layer.session

    def commit(self):
        self.layer.commit()
