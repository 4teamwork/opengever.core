from datetime import datetime
from ftw.builder.builder import Builder
from ftw.builder.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone import api


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

    @browsing
    def test_modifying_content_touches_all_dossiers_in_path(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier).touched))

        with freeze(datetime(2020, 6, 12)):
            browser.open(self.subdocument, view="edit")
            browser.fill({u"Title": "Modified subdocument"}).save()
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier).touched))

    @browsing
    def test_adding_content_touches_all_dossiers_in_path(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier).touched))

        with freeze(datetime(2020, 6, 12)):
            create(Builder('document').within(self.subdossier))
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier).touched))

    @browsing
    def test_deleting_content_touches_all_dossiers_in_path(self, browser):
        self.login(self.manager, browser=browser)

        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subsubdossier).touched))

        with freeze(datetime(2020, 6, 12)):
            api.content.delete(obj=self.subsubdocument)
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subsubdossier).touched))

    @browsing
    def test_moving_content_touches_all_dossiers_in_path(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier).touched))
        self.assertIsNone(IDossier(self.subdossier2).touched)

        with freeze(datetime(2020, 6, 12)):
            api.content.move(source=self.subdocument, target=self.subdossier2)
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier2).touched))
