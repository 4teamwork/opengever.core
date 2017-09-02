from opengever.testing import MEMORY_DB_LAYER
import unittest2


class ActivityTestCase(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    @property
    def session(self):
        return self.layer.session

    def commit(self):
        self.layer.commit()
