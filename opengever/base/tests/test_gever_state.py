from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from plone.app.testing import applyProfile


class TestGeverStateView(IntegrationTestCase):

    def setUp(self):
        super(TestGeverStateView, self).setUp()
        get_current_admin_unit().public_url = 'http://foo.org/cluster'

    def test_cluster_base_url(self):
        self.assertEquals(
            'http://foo.org/cluster/',
            self.portal.restrictedTraverse('@@gever_state/cluster_base_url')())

    def test_gever_portal_url(self):
        self.assertEquals(
            'http://foo.org/cluster/portal',
            self.portal.restrictedTraverse('@@gever_state/gever_portal_url')())

    def test_cas_server_url(self):
        applyProfile(self.portal, 'opengever.setup:casauth')
        self.assertEquals(
            'http://foo.org/cluster/portal',
            self.portal.restrictedTraverse('@@gever_state/cas_server_url')(),
        )

    @browsing
    def test_properties_action_only_available_on_types_with_different_default_view(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier, 'tabbed_view')
        self.assertIn(
            'Properties',
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)

        browser.open(self.tasktemplate, 'view')
        self.assertNotIn(
            'Properties',
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)

    @browsing
    def test_properties_action_not_available_on_portal(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal)
        self.assertNotIn(
            'Properties',
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)

    @browsing
    def test_properties_action_not_available_on_yearfolder(self, browser):
        self.login(self.manager, browser=browser)
        yearfolder = create(Builder('yearfolder').within(self.inbox))

        browser.open(yearfolder)
        self.assertNotIn(
            'Properties',
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)

    @browsing
    def test_properties_action_not_available_on_contactfolder(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.contactfolder)
        self.assertNotIn(
            'Properties',
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)

    @browsing
    def test_properties_action_not_available_for_teams(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.contactfolder, view='team-1/view')
        self.assertNotIn(
            'Properties',
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)
