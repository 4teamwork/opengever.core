from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestParticipationTab(IntegrationTestCase):

    @browsing
    def test_is_plone_object_implementation_when_contact_feature_is_disabled(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.dossier, view='tabbed_view')
        browser.click_on('Participants')

        self.assertEqual('http://nohost/plone/dossier-1/tabbed_view#participants',
                         browser.url)


class TestContactParticipationTab(IntegrationTestCase):

    features = ('contact',)

    @browsing
    def test_is_sql_object_implementation_when_contact_feature_is_enabled(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.dossier, view='tabbed_view')
        browser.click_on('Participations')

        self.assertEqual(
            'http://nohost/plone/dossier-1/tabbed_view#participations',
            browser.url)
