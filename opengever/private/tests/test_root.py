from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser import InsufficientPrivileges
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase
from plone import api


class TestPrivateRoot(IntegrationTestCase):

    @browsing
    def test_is_addable_on_plone_site(self, browser):
        self.login(self.manager, browser=browser)
        self.enable_languages()

        browser.open()
        factoriesmenu.add('Private Root')
        browser.fill({'Title (German)': u'Meine Ablage',
                      'Title (French)': u'Mon d\xe9p\xf4t',
                      'Title (English)': u'My f\xf4lder'})
        browser.click_on('Save')

        self.assertEquals([u'My f\xf4lder'], browser.css('h1').text)

        placeful_workflow = api.portal.get_tool('portal_placeful_workflow')
        config = placeful_workflow.getWorkflowPolicyConfig(browser.context)
        self.assertEqual(
            "opengever_private_policy", config.getPolicyInId())
        self.assertEqual(
            "opengever_private_policy", config.getPolicyBelowId())

    @browsing
    def test_is_only_addable_by_manager(self, browser):
        self.login(self.regular_user, browser=browser)
        self.enable_languages()

        with self.assertRaises(InsufficientPrivileges):
            browser.open(self.portal, view='++add++opengever.private.root')
            browser.fill({'Title (German)': u'Meine Ablage',
                          'Title (French)': u'Mon d\xe9p\xf4t'})
            browser.click_on('Save')

    @browsing
    def test_is_excluded_from_the_navigation(self, browser):
        self.login(self.manager, browser=browser)
        create(Builder('private_root').titled(u'Meine Ablage'))
        browser.open()
        self.assertNotIn('meine-ablage',
                         browser.css('#portal-globalnav li').text)

    @browsing
    def test_portlet_inheritance_is_blocked(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(self.private_root)

        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', browser.context)
