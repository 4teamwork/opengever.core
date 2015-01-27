from opengever.activity.models.activity import Activity
from opengever.activity.models.resource import Resource
from opengever.activity.tests.base import ActivityTestCase
from opengever.base.oguid import Oguid


class TestActivity(ActivityTestCase):

    def test_add_activity(self):
        resource = Resource(oguid=Oguid('fd','123'))
        activity = Activity(kind='TASK_ADDED', actor_id='hugo.boss',
                            description=u'sdifsdf', resource=resource)

        self.assertEquals(resource, activity.resource)
