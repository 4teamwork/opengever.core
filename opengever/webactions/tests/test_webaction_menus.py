from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
from ftw.testbrowser import browsing
from opengever.base.menu import OGCombinedActionsWorkflowMenu
from opengever.testing import IntegrationTestCase
from opengever.webactions.storage import get_storage
from opengever.webactions.tests.test_webactions_provider import TestWebActionBase
from urllib import urlencode


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
        params = urlencode({'context': self.dossier.absolute_url(), 'orgunit': 'fa'})
        self.assertEqual('http://example.org/endpoint?{}'.format(params),
                         action1.get("href"))
        self.assertEqual('http://example.org/endpoint2?{}'.format(params),
                         action2.get("href"))

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


class TestWebActionsFactoryMenus(IntegrationTestCase):

    BASE64_ENCODED_PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=='  # noqa
    icon_data = 'data:image/png;base64,%s' % BASE64_ENCODED_PNG

    def setUp(self):
        super(TestWebActionsFactoryMenus, self).setUp()
        create(Builder('webaction')
               .titled(u'\xc4ction 1')
               .having(order=1,
                       display='add-menu',
                       icon_name="fa-helicopter"))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=5,
                       display='add-menu',
                       target_url="http://example.org/endpoint2",
                       icon_data=self.icon_data))

        # Webactions are displayed in add menu of contentish objects.
        # The factory menus are overwritten separately for different
        # content types, so we test for each overwritten menu.
        with self.login(self.administrator):
            self.contentish_objects = [self.dossier, self.inbox,
                                       self.dossiertemplate, self.task,
                                       self.branch_repofolder]

    def test_webactions_are_shown_in_factory_menus(self):
        self.login(self.administrator)

        for obj in self.contentish_objects:
            menu = FactoriesMenu(obj)
            menu_items = menu.getMenuItems(obj, self.dossier.REQUEST)
            self.assertIn(u'\xc4ction 1', [item.get('title') for item in menu_items])
            self.assertIn("Action 2", [item.get('title') for item in menu_items])

    def test_only_webactions_with_display_add_menu_are_shown_in_factory_menus(self):
        self.login(self.administrator)

        storage = get_storage()
        storage.update(1, {"display": "action-buttons"})

        for obj in self.contentish_objects:
            menu = FactoriesMenu(obj)
            menu_items = menu.getMenuItems(obj, self.dossier.REQUEST)
            self.assertIn(u'\xc4ction 1', [item.get('title') for item in menu_items])
            self.assertNotIn("Action 2", [item.get('title') for item in menu_items])

    def test_webactions_are_shown_at_end_of_factory_menu(self):
        self.login(self.administrator)

        for obj in self.contentish_objects:
            menu = FactoriesMenu(obj)
            webaction_menu_items = menu.getMenuItems(obj, self.dossier.REQUEST)[-2:]
            self.assertIn(u'\xc4ction 1', [item.get('title') for item in webaction_menu_items])
            self.assertIn("Action 2", [item.get('title') for item in webaction_menu_items])

    @browsing
    def test_webaction_representations(self, browser):
        self.login(self.administrator, browser=browser)

        for obj in self.contentish_objects:
            browser.open(obj)
            action_menu = browser.css('#contentActionMenus a')
            webactions = action_menu.css('.webaction')

            action1, action2 = webactions
            params = urlencode({'context': obj.absolute_url(), 'orgunit': 'fa'})
            # check that they point to correct url
            self.assertEqual('http://example.org/endpoint?{}'.format(params),
                             action1.get("href"))
            self.assertEqual('http://example.org/endpoint2?{}'.format(params),
                             action2.get("href"))

            # check the displayed title
            self.assertEqual(u'\xc4ction 1', action1.text)
            self.assertEqual('Action 2', action2.text)

            # check icon_name attribute becomes a css class on the displayed action
            self.assertItemsEqual(["webaction", "fa-helicopter"], action1.classes)
            self.assertItemsEqual(["webaction"], action2.classes)

            # check icon_data is displayed in an img tag
            self.assertEqual([], action1.css("img"))
            self.assertEqual(1, len(action2.css("img")))

            image = action2.css("img").first
            self.assertEqual(self.icon_data, image.get("src"))

    @browsing
    def test_webactions_are_html_escaped(self, browser):
        storage = get_storage()
        storage.update(1, {"title": u"<bold>Action 2 with html</bold>"})

        self.login(self.administrator, browser=browser)
        for obj in self.contentish_objects:
            browser.open(obj)
            action_menu = browser.css('#contentActionMenus a')
            webaction_items = action_menu.css('.webaction')

            self.assertIn(u'\xc4ction 1', webaction_items[0].innerHTML)
            self.assertIn("&lt;bold&gt;Action 2 with html&lt;/bold&gt;",
                          webaction_items[1].innerHTML)
