from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestRetentionExpirationDate(FunctionalTestCase):

    def setUp(self):
        super(TestRetentionExpirationDate, self).setUp()
        self.dossier = create(Builder('dossier')
                              .having(end=date(2010, 02, 21),
                                      retention_period=20))

    def test_is_the_retention_period_years_added_to_the_end_date(self):
        self.assertEqual(date(2030, 02, 21),
                         self.dossier.get_retention_expiration_date())
