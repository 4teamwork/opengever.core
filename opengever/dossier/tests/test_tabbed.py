from ftw.testbrowser import browsing
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.testing import IntegrationTestCase
from plone import api


class TestParticipationTab(IntegrationTestCase):

    @browsing
    def test_is_plone_object_implementation_when_contact_feature_is_disabled(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.dossier, view='tabbed_view')
        browser.click_on('Participants')

        self.assertEqual(
            'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/#participants',
            browser.url)


class TestContactParticipationTab(IntegrationTestCase):

    features = ('contact',)

    @browsing
    def test_is_sql_object_implementation_when_contact_feature_is_enabled(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.dossier, view='tabbed_view')
        browser.click_on('Participations')

        self.assertEqual(
            'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/#participations',
            browser.url)


class TestDossierTabbedView(IntegrationTestCase):

    @browsing
    def test_subdossier_tab_only_shown_where_subdossiers_are_addable(self, browser):
        """When respect_max_depth flag is enabled the subdossier tab should
        only be visible on dossiers where the maximum depth allows subdossiers.
        """
        api.portal.set_registry_record(name='respect_max_depth', interface=IDossierTemplateSettings, value=True)
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='tabbed_view')
        self.assertIn('Subdossiers', browser.css('.formTab').text)
        browser.open(self.subdossier, view='tabbed_view')
        self.assertIn('Subdossiers', browser.css('.formTab').text)
        browser.open(self.subsubdossier, view='tabbed_view')
        self.assertNotIn('Subdossiers', browser.css('.formTab').text)

    @browsing
    def test_subdossier_tab_always_shown_when_dossier_contains_subdossier(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.subdossier, view='tabbed_view')
        self.assertIn('Subdossiers', browser.css('.formTab').text)
        browser.open(self.subsubdossier, view='tabbed_view')
        self.assertNotIn('Subdossiers', browser.css('.formTab').text)
