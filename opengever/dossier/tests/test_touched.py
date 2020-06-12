from datetime import datetime
from ftw.builder.builder import Builder
from ftw.builder.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase


class TestDossierTouched(IntegrationTestCase):

    @browsing
    def test_touched_date_is_empty_by_default(self, browser):
        self.login(self.administrator, browser)
        dossier = create(Builder("dossier")
                         .within(self.branch_repofolder))
        self.assertIsNone(IDossier(dossier).touched)

    @browsing
    def test_touched_date_is_not_updated_on_the_same_day(self, browser):
        self.login(self.administrator, browser=browser)

        # Multiple modifications on the same day result in the same touched
        # date. This is mostly implicit by the usage of a date field instead
        # of a datetime field.
        with freeze(datetime(2020, 6, 12)):
            browser.open(self.dossier, view="edit")
            browser.fill({u"Title": "First modification"}).save()
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))

            browser.open(self.dossier, view="edit")
            browser.fill({u"Title": "Modification on the same day"}).save()
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))

        # Modifications on the next day will change the "touched" date.
        with freeze(datetime(2020, 6, 13)):
            browser.open(self.dossier, view="edit")
            browser.fill({u"Title": "Modification on the next day"}).save()
            self.assertEqual("2020-06-13", str(IDossier(self.dossier).touched))
