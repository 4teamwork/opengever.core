from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase


class TestBlockedLocalRolesListing(IntegrationTestCase):

    @browsing
    def test_blocked_role_tab_not_visible_on_repository_root(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.regular_user, browser)

        browser.open(self.repository_root)
        self.assertNotIn(
            u'Gesch\xfctzte Objekte',
            browser.css('.tabbedview-tabs a').text
            )

    @browsing
    def test_blocked_role_tab_not_visible_on_repository_folder(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.regular_user, browser)

        browser.open(self.branch_repofolder)
        self.assertNotIn(
            u'Gesch\xfctzte Objekte',
            browser.css('.tabbedview-tabs a').text
            )

    @browsing
    def test_blocked_role_tab_not_visible_on_dossier(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.regular_user, browser)

        browser.open(self.dossier)
        self.assertNotIn(
            u'Gesch\xfctzte Objekte',
            browser.css('.tabbedview-tabs a').text
            )

    @browsing
    def test_blocked_role_tab_visible_for_manager_on_repository_root(self, browser):  # noqa
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.manager, browser)

        browser.open(self.repository_root)
        self.assertIn(
            u'Gesch\xfctzte Objekte',
            browser.css('.tabbedview-tabs a').text
            )

    @browsing
    def test_blocked_role_tab_visible_for_manager_on_repository_folder(self, browser):  # noqa
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.manager, browser)

        browser.open(self.branch_repofolder)
        self.assertIn(
            u'Gesch\xfctzte Objekte',
            browser.css('.tabbedview-tabs a').text
            )

    @browsing
    def test_blocked_role_tab_visible_for_manager_on_dossier(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.manager, browser)

        browser.open(self.dossier)
        self.assertIn(
            u'Gesch\xfctzte Objekte',
            browser.css('.tabbedview-tabs a').text
            )

    @browsing
    def test_blocked_role_tab_visible_for_administrator_on_repository_root(self, browser):  # noqa
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.administrator, browser)

        browser.open(self.repository_root)
        self.assertIn(
            u'Gesch\xfctzte Objekte',
            browser.css('.tabbedview-tabs a').text
            )

    @browsing
    def test_blocked_role_tab_visible_for_administrator_on_repository_folder(self, browser):  # noqa
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.administrator, browser)

        browser.open(self.branch_repofolder)
        self.assertIn(
            u'Gesch\xfctzte Objekte',
            browser.css('.tabbedview-tabs a').text
            )

    @browsing
    def test_blocked_role_tab_visible_for_administrator_on_dossier(self, browser):  # noqa
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.administrator, browser)

        browser.open(self.dossier)
        self.assertIn(
            u'Gesch\xfctzte Objekte',
            browser.css('.tabbedview-tabs a').text
            )

    @browsing
    def test_blocked_role_tab_does_not_render_tree_when_nothing_found(self, browser):  # noqa
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.administrator, browser)
        browser.open(self.empty_repofolder, view="tabbedview_view-blocked-local-roles")
        self.assertEquals(
            browser.css('.blocked-local-roles-listing').first.text,
            u'Keine gesch\xfctzte Objekte in diesem Bereich gefunden.',
            )

    @browsing
    def test_blocked_role_tab_does_not_render_tree_for_regular_user(self, browser):  # noqa
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.regular_user, browser)

        self.dossier.__ac_local_roles_block__ = True
        self.dossier.reindexObject(idxs=['blocked_local_roles'])

        with browser.expect_http_error(reason='OK'):
            browser.open(
                self.repository_root,
                view="tabbedview_view-blocked-local-roles",
                )

    @browsing
    def test_blocked_role_tab_does_renders_tree_for_manager(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.administrator, browser)

        self.dossier.__ac_local_roles_block__ = True
        self.dossier.reindexObject(idxs=['blocked_local_roles'])

        browser.open(
            self.repository_root,
            view="tabbedview_view-blocked-local-roles",
            )
        self.assertEquals(
            browser.css('.blocked-local-roles-listing a').first.text,
            u'1. F\xfchrung',
            )

    @browsing
    def test_blocked_role_tab_does_renders_tree_for_administrator(self, browser):  # noqa
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.manager, browser)

        self.dossier.__ac_local_roles_block__ = True
        self.dossier.reindexObject(idxs=['blocked_local_roles'])

        browser.open(
            self.repository_root,
            view="tabbedview_view-blocked-local-roles",
            )
        self.assertEquals(
            browser.css('.blocked-local-roles-listing a').first.text,
            u'1. F\xfchrung',
            )

    @browsing
    def test_blocked_role_tab_tree_rendering(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.administrator, browser)
        browser.open(self.repository_root, view="tabbedview_view-blocked-local-roles")
        expected_titles = [
            u'1. F\xfchrung',
            u'1.1. Vertr\xe4ge und Vereinbarungen',
            u'Luftsch\xfctze',
            u'Zu allem \xdcbel',
            ]
        self.assertEquals(expected_titles, browser.css('.blocked-local-roles-link').text)
        expected_titles = [
            u'1.1. Vertr\xe4ge und Vereinbarungen',
            u'Luftsch\xfctze',
            u'Zu allem \xdcbel',
            ]
        self.assertEquals(expected_titles, browser.css('.level1 a').text)
        expected_titles = [u'Luftsch\xfctze', u'Zu allem \xdcbel']
        self.assertEquals(expected_titles, browser.css('.level2 a').text)
        self.assertFalse(browser.css('.level3 a').text)
        nodes = browser.css('.blocked-local-roles-link')
        repo = 'contenttype-opengever-repository-repositoryfolder'
        dossier = 'contenttype-opengever-dossier-businesscasedossier'
        self.assertIn(repo, nodes[0].classes)
        self.assertIn(repo, nodes[1].classes)
        self.assertIn(dossier, nodes[2].classes)

    @browsing
    def test_blocked_role_tab_can_drill_down_to_dossier(self, browser):
        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.administrator, browser)
        browser.open(self.repository_root, view="tabbedview_view-blocked-local-roles")
        browser.css('.blocked-local-roles-link').first.click()
        expected_url = ''.join((self.branch_repofolder.absolute_url(), '#blocked-local-roles', ))
        self.assertEquals(expected_url, browser.url)
        browser.open(self.branch_repofolder, view="tabbedview_view-blocked-local-roles")
        browser.css('.blocked-local-roles-link').first.click()
        expected_url = ''.join((self.leaf_repofolder.absolute_url(), '#blocked-local-roles', ))
        self.assertEquals(expected_url, browser.url)
        browser.open(self.leaf_repofolder, view="tabbedview_view-blocked-local-roles")
        browser.css('.blocked-local-roles-link').first.click()
        expected_url = ''.join((self.protected_dossier.absolute_url(), '#sharing', ))
        self.assertEquals(expected_url, browser.url)

    @browsing
    def test_protected_dossiers_are_listed_for_manager(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'})
        form = browser.find_form_by_field('Reading')
        form.find_widget('Reading and writing').fill(self.regular_user.getId())
        browser.click_on('Save')
        new_dossier = browser.context

        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.manager, browser)

        browser.open(
            self.repository_root,
            view="tabbedview_view-blocked-local-roles",
            )

        self.assertIn(
            new_dossier.title,
            browser.css('.level2').text[0],
            )

    @browsing
    def test_protected_dossiers_are_listed_for_administrator(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'})
        form = browser.find_form_by_field('Reading')
        form.find_widget('Reading and writing').fill(self.regular_user.getId())
        browser.click_on('Save')
        new_dossier = browser.context

        browser.append_request_header('Accept-Language', 'de-ch')
        self.login(self.administrator, browser)

        browser.open(
            self.repository_root,
            view="tabbedview_view-blocked-local-roles",
            )

        self.assertIn(
            new_dossier.title,
            browser.css('.level2').text[0],
            )
