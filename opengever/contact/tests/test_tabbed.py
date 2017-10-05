from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.contact.interfaces import IContactSettings
from opengever.core.testing import toggle_feature
from opengever.testing import FunctionalTestCase


class TestContactFolderTabbedView(FunctionalTestCase):

    def setUp(self):
        super(TestContactFolderTabbedView, self).setUp()
        self.contactfolder = create(Builder('contactfolder')
                                    .titled(u'Kontakte'))

    @browsing
    def test_shows_local_and_user_tab(self, browser):
        browser.login().open(self.contactfolder, view='tabbed_view')

        self.assertEquals(
            ['Local', 'Users', 'Teams'],
            browser.css('.formTab').text)

    @browsing
    def test_shows_person_organization_and_user_tab_when_contact_feature_is_enabled(self, browser):
        toggle_feature(IContactSettings, enabled=True)
        browser.login().open(self.contactfolder, view='tabbed_view')

        self.assertEquals(
            ['Persons', 'Organizations', 'Users', 'Teams'],
            browser.css('.formTab').text)
