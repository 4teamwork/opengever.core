from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.menu import OGCombinedActionsWorkflowMenu
from opengever.testing import IntegrationTestCase
from opengever.webactions.storage import get_storage
from opengever.webactions.tests.test_webactions_provider import TestWebActionBase


class TestWebActionsTitleButtons(IntegrationTestCase):

    BASE64_ENCODED_PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=='  # noqa
    icon_data = 'data:image/png;base64,%s' % BASE64_ENCODED_PNG

    def setUp(self):
        super(TestWebActionsTitleButtons, self).setUp()
        create(Builder('webaction')
               .titled(u'\xc4ction 1')
               .having(order=1,
                       display='title-buttons',
                       icon_name="fa-helicopter"))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=5,
                       display='title-buttons',
                       target_url="http://example.org/endpoint2",
                       icon_data=self.icon_data))

    @browsing
    def test_webactions_are_shown_on_dexterity_object(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        viewlet = browser.css('#webactions-title-buttons').first
        self.assertIsNotNone(viewlet)
        self.assertIn(u"\xc4ction 1", viewlet.innerHTML)
        self.assertIn("Action 2", viewlet.innerHTML)

    @browsing
    def test_webactions_are_disabled_on_wrapper_objects(self, browser):
        self.activate_feature('meeting')
        self.login(self.meeting_user, browser=browser)
        browser.open(self.meeting)

        viewlet = browser.css('#webactions-title-buttons').first
        self.assertEqual(u"", viewlet.innerHTML.strip())

    @browsing
    def test_webactions_representations(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        viewlet = browser.css('#webactions-title-buttons')
        webactions = viewlet.css("a")
        self.assertEqual(len(webactions), 2)

        action1, action2 = webactions
        self.assertEqual('http://example.org/endpoint', action1.get("href"))
        self.assertEqual('http://example.org/endpoint2', action2.get("href"))

        self.assertEqual(u'\xc4ction 1', action1.get("title"))
        self.assertEqual('Action 2', action2.get("title"))

        self.assertItemsEqual(["webaction_button", "fa", "fa-helicopter"], action1.classes)
        self.assertItemsEqual(["webaction_button"], action2.classes)

        self.assertEqual([], action1.css("img"))
        self.assertEqual(1, len(action2.css("img")))

        image = action2.css("img").first
        self.assertEqual(self.icon_data, image.get("src"))

    @browsing
    def test_webactions_are_html_escaped(self, browser):
        storage = get_storage()
        storage.update(1, {"title": u"<bold>Action 2 with html</bold>"})

        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        viewlet = browser.css('#webactions-title-buttons').first
        self.assertIn(u"\xc4ction 1", viewlet.innerHTML)
        self.assertIn("&lt;bold&gt;Action 2 with html&lt;/bold&gt;", viewlet.innerHTML)

    @browsing
    def test_only_webactions_with_display_title_buttons_are_shown(self, browser):
        storage = get_storage()
        storage.update(1, {"display": "action-buttons"})
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        viewlet = browser.css('#webactions-title-buttons')
        webactions = viewlet.css("a")
        self.assertEqual(len(webactions), 1)
        self.assertEqual([u"\xc4ction 1"],
                         map(lambda action: action.get("title"), webactions))


class TestWebactionsActionsMenu(TestWebActionBase):

    def setUp(self):
        super(TestWebactionsActionsMenu, self).setUp()
        create(Builder('webaction')
               .titled(u'\xc4ction 1')
               .having(order=5,
                       enabled=True,
                       display='actions-menu'))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=1,
                       enabled=True,
                       display='actions-menu',
                       target_url="http://example.org/endpoint2"))

    @browsing
    def test_webactions_are_shown_on_dexterity_object(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        action_menu = browser.css('#contentActionMenus a')
        webaction_items = action_menu.css('.actionicon-object_webaction')
        self.assertEqual(['Action 2', u'\xc4ction 1'], webaction_items.text)

    @browsing
    def test_webactions_are_disabled_on_wrapper_objects(self, browser):
        self.activate_feature('meeting')
        self.login(self.meeting_user, browser=browser)
        browser.open(self.meeting)

        action_menu = browser.css('#contentActionMenus a')
        webaction_items = action_menu.css('.actionicon-object_webaction')
        self.assertEqual([], webaction_items.text)

    def test_only_webactions_with_display_actions_menu_are_shown(self):
        self.login(self.regular_user)
        menu = OGCombinedActionsWorkflowMenu(self.dossier)

        menu_items = menu.getMenuItems(self.dossier, self.dossier.REQUEST)
        webaction_items = filter(
            lambda item: item.get("extra").get("class") == 'actionicon-object_webaction',
            menu_items)

        self.assertEqual(['Action 2', u'\xc4ction 1'],
                         [action["title"] for action in webaction_items])

        storage = get_storage()
        storage.update(1, {"display": "action-buttons"})
        self.clear_request_cache()

        menu_items = menu.getMenuItems(self.dossier, self.dossier.REQUEST)
        webaction_items = filter(
            lambda item: item.get("extra").get("class") == 'actionicon-object_webaction',
            menu_items)

        self.assertEqual([u'\xc4ction 1'],
                         [action["title"] for action in webaction_items])

    @browsing
    def test_webactions_are_html_escaped(self, browser):
        storage = get_storage()
        storage.update(1, {"title": u"<bold>Action 2 with html</bold>"})

        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)

        action_menu = browser.css('#contentActionMenus a')
        webaction_items = action_menu.css('.actionicon-object_webaction')

        self.assertIn(u'\xc4ction 1', webaction_items[1].innerHTML)
        self.assertIn("&lt;bold&gt;Action 2 with html&lt;/bold&gt;",
                      webaction_items[0].innerHTML)

    def test_only_webactions_satisfying_type_are_shown(self):
        self.login(self.regular_user)

        storage = get_storage()
        storage.update(0, {"types": ["opengever.document.document"]})
        storage.update(1, {"types": ["opengever.dossier.businesscasedossier"]})
        menu = OGCombinedActionsWorkflowMenu(self.dossier)

        menu_items = menu.getMenuItems(self.dossier, self.dossier.REQUEST)
        webaction_items = filter(
            lambda item: item.get("extra").get("class") == 'actionicon-object_webaction',
            menu_items)

        self.assertEqual(['Action 2'],
                         [action["title"] for action in webaction_items])

        self.clear_request_cache()
        menu_items = menu.getMenuItems(self.document, self.document.REQUEST)
        webaction_items = filter(
            lambda item: item.get("extra").get("class") == 'actionicon-object_webaction',
            menu_items)

        self.assertEqual([u'\xc4ction 1'],
                         [action["title"] for action in webaction_items])
