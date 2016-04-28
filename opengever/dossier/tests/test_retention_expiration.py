from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import obj2brain
import transaction


class TestRetentionExpirationDate(FunctionalTestCase):

    def setUp(self):
        super(TestRetentionExpirationDate, self).setUp()
        self.dossier = create(Builder('dossier')
                              .having(start=date(2010, 2, 18),
                                      end=date(2010, 2, 21),
                                      retention_period=20))

    def test_is_the_retention_period_years_added_to_the_end_date(self):
        self.assertEqual(date(2030, 2, 21),
                         self.dossier.get_retention_expiration_date())

    @browsing
    def test_is_updated_when_resolving_a_dossier(self, browser):
        self.grant('Reader', 'Contributor',  'Editor', 'Reviewer')

        with freeze(datetime(2010, 2, 21)):
            IDossier(self.dossier).end = date(2010, 2, 25)
            transaction.commit()

            browser.login().open(self.dossier)
            browser.find('dossier-transition-resolve').click()
            self.assertEqual(date(2030, 2, 25),
                             self.dossier.get_retention_expiration_date())
            self.assertEqual(date(2030, 2, 25),
                             obj2brain(self.dossier).retention_expiration)

    @browsing
    def test_index_is_updated_when_end_date_is_changed_during_resolving(self, browser):
        self.grant('Reader', 'Contributor',  'Editor', 'Reviewer')

        create(Builder('document')
               .within(self.dossier)
               .having(document_date=date(2015, 1, 1)))

        former_indexed_value = index_data_for(self.dossier).get('retention_expiration')

        browser.login().open(self.dossier)
        browser.find('dossier-transition-resolve').click()

        self.assertNotEqual(
            former_indexed_value,
            index_data_for(self.dossier).get('retention_expiration'))

    def test_is_expired_when_its_earlier_than_today(self):
        with freeze(datetime(2030, 2, 22)):
            self.assertTrue(self.dossier.is_retention_period_expired())

    def test_is_expired_when_its_today(self):
        with freeze(datetime(2030, 2, 21)):
            self.assertTrue(self.dossier.is_retention_period_expired())

    def test_is_not_expired_when_its_later_than_today(self):
        with freeze(datetime(2030, 2, 18)):
            self.assertFalse(self.dossier.is_retention_period_expired())
