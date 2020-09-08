from datetime import date
from ftw.testbrowser import browsing
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest
from opengever.api.ogdslistingbase import OGDSListingBaseService


class TestOGDSListingBaseService(IntegrationTestCase):


    def test_all_subclasses_define_unique_sort_on(self):
        """We want to make sure that all OGDS listings define unique_sort_on
        to guarantees consistent responses for successive queries. This is essential
        to avoid some items being returned multiple times and others missing.
        """
        self.assertIsNone(OGDSListingBaseService.unique_sort_on)
        for subclass in OGDSListingBaseService.__subclasses__():
            self.assertIsNotNone(subclass.unique_sort_on)
