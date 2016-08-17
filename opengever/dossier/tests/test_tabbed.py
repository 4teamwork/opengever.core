from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.contact.interfaces import IContactSettings
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestParticipationTab(FunctionalTestCase):

    def setUp(self):
        super(TestParticipationTab, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_is_plone_object_implementation_when_contact_feature_is_disabled(self, browser):
        api.portal.set_registry_record(
            'is_feature_enabled', False, interface=IContactSettings)
        transaction.commit()

        browser.login().open(self.dossier, view='tabbed_view')
        browser.click_on('Participants')

        self.assertEqual('http://nohost/plone/dossier-1/tabbed_view#participants',
                         browser.url)

    @browsing
    def test_is_sql_object_implementation_when_contact_feature_is_enabled(self, browser):
        api.portal.set_registry_record(
            'is_feature_enabled', True, interface=IContactSettings)
        transaction.commit()

        browser.login().open(self.dossier, view='tabbed_view')
        browser.click_on('Participations')

        self.assertEqual(
            'http://nohost/plone/dossier-1/tabbed_view#participations',
            browser.url)
