from opengever.ogds.models.testing import DATABASE_LAYER
import unittest2


class OGDSTestCase(unittest2.TestCase):

    layer = DATABASE_LAYER

    @property
    def session(self):
        return self.layer.session

    def commit(self):
        self.layer.commit()
