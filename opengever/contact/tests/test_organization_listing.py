from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestOrganizationListing(FunctionalTestCase):

    def setUp(self):
        super(TestOrganizationListing, self).setUp()

        self.contactfolder = create(Builder('contactfolder')
                                    .titled(u'Kontakte'))

        create(Builder('organization').named(u'Meier AG'))
        create(Builder('organization')
               .named(u'M\xfcller')
               .having(is_active=False))
        create(Builder('organization').named(u'AAA Design'))

    @browsing
    def test_lists_only_active_organizations_by_default(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-organizations')

        self.assertEquals(
            [[u'Name', 'Active'],
             [u'AAA Design', 'Yes'],
             [u'Meier AG', 'Yes']],
            browser.css('.listing').first.lists())

    @browsing
    def test_includes_inactive_organizations_with_the_all_filter(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-organizations',
            data={'organization_state_filter': 'filter_all'})

        self.assertEquals(
            [[u'Name', 'Active'],
             [u'AAA Design', 'Yes'],
             [u'Meier AG', 'Yes'],
             [u'M\xfcller', 'No']],
            browser.css('.listing').first.lists())

    @browsing
    def test_name_is_linked_to_organization_view(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-organizations')

        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/organization-1/view',
            browser.find(u'Meier AG').get('href'))

    @browsing
    def test_filtering_on_name(self, browser):
        browser.login().open(
            self.contactfolder,
            view='tabbedview_view-organizations',
            data={'searchable_text': 'Design'})

        self.assertEquals(
            [[u'Name', 'Active'],
             [u'AAA Design', 'Yes']],
            browser.css('.listing').first.lists())
