from opengever.testing import MEMORY_DB_LAYER
import unittest


class ActivityTestCase(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    @property
    def session(self):
        return self.layer.session

    def commit(self):
        self.layer.commit()
