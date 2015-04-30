from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase


class TestRegressionPloneformMacros(FunctionalTestCase):

    def setUp(self):
        super(TestRegressionPloneformMacros, self).setUp()

        self.repository_root = create(Builder('repository_root'))
        self.repository_folder = create(
            Builder('repository').within(self.repository_root))

    @browsing
    def test_error_messages_are_displayed_for_form_groups(self, browser):
        browser.login()

        # make sure that only title is required
        # ensure that our assumption is correct, otherwise the regression
        # test won't work correctly
        browser.open(self.repository_folder,
                     view='++add++opengever.dossier.businesscasedossier')
        browser.fill({'Title': 'foo'})
        browser.find('Save').click()
        self.assertEqual(['Item created'], info_messages())

        # actually test that group-errors are displayed correctly
        browser.open(self.repository_folder,
                     view='++add++opengever.dossier.businesscasedossier')
        # fill invalid
        browser.fill({'Title': 'foo', 'Date of cassation': 'invalid'})
        browser.find('Save').click()
        self.assertEqual([], info_messages())
        self.assertEqual(['There were some errors.'], error_messages())
