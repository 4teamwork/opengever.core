from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.webactions.browser.manage_webactions import ManageWebactionsView
from opengever.webactions.storage import get_storage
from plone import api


class TestReturnedWebactions(IntegrationTestCase):

    def setUp(self):
        super(TestReturnedWebactions, self).setUp()

        with self.login(self.webaction_manager):
            with freeze(datetime(2018, 4, 20)):
                create(Builder('webaction')
                       .titled(u'Action 1')
                       .having(order=5))

            with freeze(datetime(2018, 4, 21)):
                create(Builder('webaction')
                       .titled(u'Action 2')
                       .having(order=10))

            with freeze(datetime(2018, 4, 22)):
                create(Builder('webaction')
                       .titled(u'Action 3')
                       .having(order=20))

        self.action1_data = {'target_url': 'http://example.org/endpoint',
                             'title': u'Action 1',
                             'display': 'actions-menu',
                             'mode': 'self',
                             'action_id': 0,
                             'order': 5,
                             'created': datetime(2018, 4, 20),
                             'modified': datetime(2018, 4, 20),
                             'owner': 'webaction.manager',
                             'scope': 'global'}

        self.action2_data = {'target_url': 'http://example.org/endpoint',
                             'title': u'Action 2',
                             'display': 'actions-menu',
                             'mode': 'self',
                             'action_id': 1,
                             'order': 10,
                             'created': datetime(2018, 4, 21),
                             'modified': datetime(2018, 4, 21),
                             'owner': 'webaction.manager',
                             'scope': 'global'}

        self.action3_data = {'target_url': 'http://example.org/endpoint',
                             'title': u'Action 3',
                             'display': 'actions-menu',
                             'mode': 'self',
                             'action_id': 2,
                             'order': 20,
                             'created': datetime(2018, 4, 22),
                             'modified': datetime(2018, 4, 22),
                             'owner': 'webaction.manager',
                             'scope': 'global'}

    def get_webactions(self):
        site = api.portal.getSite()
        management_view = ManageWebactionsView(site, self.request)
        return management_view._get_webactions()

    def test_returned_webactions(self):
        """ This test also asserts the initial state and returned
        data, serving as basis for the other tests in this class.
        """
        self.login(self.webaction_manager)

        webactions = self.get_webactions()
        expected_data = [self.action1_data, self.action2_data, self.action3_data]

        self.assertEqual(expected_data, webactions)

    def test_returns_only_actions_owned_by_user(self):
        self.login(self.webaction_manager)

        storage = get_storage()
        storage._actions[1]["owner"] = self.regular_user.id

        expected_data = [self.action1_data, self.action3_data]

        self.assertEqual(expected_data, self.get_webactions())

    def test_returns_all_actions_for_managers(self):
        self.login(self.manager)

        storage = get_storage()
        storage._actions[1]["owner"] = self.regular_user.id

        self.action2_data["owner"] = self.regular_user.id
        expected_data = [self.action1_data, self.action2_data, self.action3_data]

        self.assertEqual(expected_data, self.get_webactions())


class TestWebactionsManagementView(IntegrationTestCase):

    def setUp(self):
        super(TestWebactionsManagementView, self).setUp()

        with self.login(self.webaction_manager):
            with freeze(datetime(2018, 4, 20)):
                create(Builder('webaction')
                       .titled(u'Action 1')
                       .having(order=5))

            with freeze(datetime(2018, 4, 21)):
                create(Builder('webaction')
                       .titled(u'<i>Action 2</i>')
                       .having(order=10))

            with freeze(datetime(2018, 4, 22)):
                create(Builder('webaction')
                       .titled(u'\xc4ction 3')
                       .having(order=20))

    @browsing
    def test_available_for_managers(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(api.portal.getSite(), view="manage-webactions")

        self.login(self.manager, browser)
        browser.open(api.portal.getSite(), view="manage-webactions")

    @browsing
    def test_available_for_webaction_managers(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(api.portal.getSite(), view="manage-webactions")

        self.login(self.webaction_manager, browser)
        browser.open(api.portal.getSite(), view="manage-webactions")

    @browsing
    def test_lists_webactions(self, browser):
        self.login(self.webaction_manager, browser)
        site = api.portal.getSite()
        browser.open(site, view="manage-webactions")
        webactions = browser.css("#webactions-list li")

        self.assertEqual(3, len(webactions))
        self.assertEqual(['0. Action 1', '1. <i>Action 2</i>', u'2. \xc4ction 3'],
                         [action.css("h4").first.text for action in webactions])

    @browsing
    def test_fields_are_html_escaped(self, browser):
        self.login(self.webaction_manager, browser)

        storage = get_storage()
        storage.update(1, {"display": "title-buttons",
                           "comment": u"with <i>html</i>",
                           "unique_name": u"with <i>html</i>",
                           "icon_name": "with <i>html</i>"})

        site = api.portal.getSite()
        browser.open(site, view="manage-webactions")
        webaction = browser.css("#webactions-list li")[1]
        fields = [item.text for item in webaction.css("p")]
        self.assertIn(u"unique_name: with <i>html</i>", fields)
        self.assertIn(u"comment: with <i>html</i>", fields)
        self.assertIn(u"icon_name: with <i>html</i> ()", fields)

    @browsing
    def test_delete_webaction(self, browser):
        self.login(self.webaction_manager, browser)
        site = api.portal.getSite()

        storage = get_storage()
        self.assertEqual(3, len(storage.list()))

        browser.open(site, view="manage-webactions")

        # check that button points to correct action
        button = browser.css("#delete-webactions").first
        self.assertEqual('action-delete-webactions', button.name)

        # test browser does not properly handle clicking multiple checkboxes
        # with the same name, so we can delete just one webaction at a time and
        # only the first in the list
        browser.fill({u'0. Action 1': True})
        browser.click_on('Delete selected webactions')

        self.assertEqual(2, len(storage.list()))
        self.assertEqual([u'<i>Action 2</i>', u'\xc4ction 3'],
                         [action["title"] for action in storage.list()])

    @browsing
    def test_edit_links_point_to_webaction_edit_view(self, browser):
        self.login(self.webaction_manager, browser)
        site = api.portal.getSite()
        browser.open(site, view="manage-webactions")
        webactions = browser.css("#webactions-list li")

        edit_url = "/".join([site.absolute_url(), "@@manage-webactions-edit?action_id={}"])
        self.assertEqual([edit_url.format(i) for i in range(3)],
                         [action.find("Edit").get("href") for action in webactions])

        webactions[0].find("Edit").click()
        self.assertEqual('Edit Webaction',
                         browser.css(".documentFirstHeading").first.text)

        form = browser.find_form_by_field("Title")
        self.assertEqual('Action 1', form.find_field("Title").value)

    @browsing
    def test_add_webaction_points_to_add_form(self, browser):
        self.login(self.webaction_manager, browser)
        site = api.portal.getSite()

        browser.open(site, view="manage-webactions")

        button = browser.find("Add new webaction")
        add_url = "/".join([site.absolute_url(), "@@manage-webactions-add"])
        self.assertEqual(button.get("href"), add_url)

        button.click()
        self.assertEqual('Add webaction',
                         browser.css(".documentFirstHeading").first.text)
