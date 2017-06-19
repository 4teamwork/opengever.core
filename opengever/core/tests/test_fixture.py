from DateTime import DateTime
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID


class TestTestingFixture(IntegrationTestCase):

    def test_ordnungssystem_has_static_creation_date(self):
        self.assertEquals(DateTime('2016/08/31 09:01:33 GMT+2'),
                          self.repository_root.created())

    def test_ordnungssystem_has_static_uuid(self):
        self.assertEquals('repotree000000000000000000000001',
                          IUUID(self.repository_root))
