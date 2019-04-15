from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.webactions.storage import get_storage
from plone import api


class TestWebactionsAddForm(IntegrationTestCase):

    @browsing
    def test_add_form_available_for_managers(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(api.portal.getSite(), view="manage-webactions-add")

        self.login(self.manager, browser)
        browser.open(api.portal.getSite(), view="manage-webactions-add")

    @browsing
    def test_add_form_available_for_webaction_managers(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(api.portal.getSite(), view="manage-webactions-add")

        self.login(self.webaction_manager, browser)
        browser.open(api.portal.getSite(), view="manage-webactions-add")

    @browsing
    def test_add_webaction_only_saves_necessary_data(self, browser):
        self.login(self.webaction_manager, browser)
        storage = get_storage()

        self.assertEqual(0, len(storage.list()))

        browser.open(api.portal.getSite(), view="manage-webactions-add")
        browser.fill({"Title": "Action 1",
                      "Target URL": "http://test.ch",
                      "Order": "5",
                      "Display Location": "action-buttons",
                      "Mode": "self",
                      "Scope": "global"})
        browser.click_on("Add webaction")

        self.assertEqual([], error_messages())
        self.assertEqual(1, len(storage.list()))
        webaction = storage.list()[0]

        expected_fields = ['target_url', 'title', 'display', 'mode',
                           'scope', 'order', 'created', 'modified',
                           'owner', 'action_id']
        self.assertItemsEqual(expected_fields, webaction.keys())

    @browsing
    def test_form_is_prefilled_with_missing_values(self, browser):
        # Enabled has a truthy missing value which needs to be prefilled
        # in the add form.
        self.login(self.webaction_manager, browser)
        storage = get_storage()

        self.assertEqual(0, len(storage.list()))

        browser.open(api.portal.getSite(), view="manage-webactions-add")
        form = browser.find_form_by_field("Enabled")
        self.assertEqual(form.find_field("Enabled").value, 'selected')

    @browsing
    def test_missing_required_field(self, browser):
        self.login(self.webaction_manager, browser)
        storage = get_storage()

        self.assertEqual(0, len(storage.list()))

        browser.open(api.portal.getSite(), view="manage-webactions-add")
        browser.fill({"Title": "Action 1",
                      "Target URL": "http://test.ch",
                      "Order": "5",
                      "Display Location": "action-buttons",
                      "Mode": "self"})
        browser.click_on("Add webaction")

        self.assertEqual(['There were some errors.'], error_messages())

        errors = browser.css("div.error")
        # The error class is added on the field itself and on the div
        # containing the error text
        self.assertEqual(2, len(errors))
        self.assertEqual('formfield-form-widgets-scope', errors[0].get("id"))
        self.assertEqual("Required input is missing.", errors[1].text)
        self.assertEqual(0, len(storage.list()))

    @browsing
    def test_missing_required_icon_invariant(self, browser):
        self.login(self.webaction_manager, browser)
        storage = get_storage()

        self.assertEqual(0, len(storage.list()))

        browser.open(api.portal.getSite(), view="manage-webactions-add")
        browser.fill({"Title": "Action 1",
                      "Target URL": "http://test.ch",
                      "Order": "5",
                      "Display Location": "title-buttons",
                      "Mode": "self",
                      "Scope": "global"})
        browser.click_on("Add webaction")

        self.assertEqual(['There were some errors.'], error_messages())

        errors = browser.css("div.error")
        self.assertEqual(1, len(errors))
        self.assertEqual("Display location 'title-buttons' requires an icon.",
                         errors.first.text)
        self.assertEqual(0, len(storage.list()))


class TestWebactionsEditForm(IntegrationTestCase):

    def setUp(self):
        super(TestWebactionsEditForm, self).setUp()

        with self.login(self.webaction_manager):
            with freeze(datetime(2018, 4, 20)):
                create(Builder('webaction')
                       .titled(u'Action 1')
                       .having(order=5))

            with freeze(datetime(2018, 4, 21)):
                create(Builder('webaction')
                       .titled(u'Action 2')
                       .having(order=10))

    def get_edit_url(self, action_id=0):
        return "/".join([api.portal.getSite().absolute_url(),
                         "manage-webactions-edit?action_id={}".format(action_id)])

    @browsing
    def test_edit_form_available_for_managers(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(self.get_edit_url())

        self.login(self.manager, browser)
        browser.open(self.get_edit_url())

    @browsing
    def test_edit_form_available_for_webaction_managers(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_unauthorized():
            browser.open(self.get_edit_url())

        self.login(self.webaction_manager, browser)
        browser.open(self.get_edit_url())

    @browsing
    def test_no_modifications(self, browser):
        self.login(self.webaction_manager, browser)

        browser.open(self.get_edit_url())
        browser.click_on("Save")

        webaction = get_storage().list()[0]
        self.assertEqual(['No changes were applied.'], info_messages())
        self.assertEqual(datetime(2018, 4, 20), webaction.get("modified"))

    @browsing
    def test_only_saves_modified_fields(self, browser):
        self.login(self.webaction_manager, browser)

        webaction_before = get_storage().list()[0]
        with freeze(datetime(2018, 4, 22)):
            browser.open(self.get_edit_url())
            browser.fill({"Title": "changed title"})
            browser.click_on("Save")

        webaction = get_storage().list()[0]
        self.assertEqual(['Data successfully updated.'], info_messages())
        self.assertNotEqual(webaction_before.pop("title"), webaction.get("title"))
        self.assertEqual("changed title", webaction.pop("title"))
        self.assertNotEqual(webaction_before.pop("modified"), webaction.get("modified"))
        self.assertEqual(datetime(2018, 4, 22), webaction.pop("modified"))
        self.assertDictEqual(webaction_before, webaction)

    @browsing
    def test_validates_individual_fields(self, browser):
        self.login(self.webaction_manager, browser)
        browser.open(self.get_edit_url())

        browser.fill({"Target URL": "not an url"})
        browser.click_on("Save")

        self.assertEqual(['There were some errors.'], error_messages())
        errors = browser.css("div.error")
        # The error class is added on the field itself and on the div
        # containing the error text
        self.assertEqual(2, len(errors))
        self.assertEqual('formfield-form-widgets-target_url', errors[0].get("id"))
        self.assertEqual('The specified URI is not valid.', errors[1].text)

        webaction = get_storage().list()[0]
        self.assertEqual(datetime(2018, 4, 20), webaction.pop("modified"))

    @browsing
    def test_missing_required_icon_invariant(self, browser):
        self.login(self.webaction_manager, browser)
        browser.open(self.get_edit_url())

        browser.fill({"Display Location": "title-buttons"})
        browser.click_on("Save")

        self.assertEqual(['There were some errors.'], error_messages())
        errors = browser.css("div.error")
        self.assertEqual(1, len(errors))
        self.assertEqual("Display location 'title-buttons' requires an icon.",
                         errors.first.text)

        webaction = get_storage().list()[0]
        self.assertEqual(datetime(2018, 4, 20), webaction.pop("modified"))
