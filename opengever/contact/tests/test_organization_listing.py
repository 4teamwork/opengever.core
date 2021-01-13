from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestOrganizationListing(FunctionalTestCase):

    def setUp(self):
        super(TestOrganizationListing, self).setUp()

        self.contactfolder = create(Builder('contactfolder')
                                    .titled(u'Kontakte'))

        create(Builder('organization')
               .having(former_contact_id=112233)
               .named(u'Meier AG'))
        create(Builder('organization')
               .named(u'M\xfcller')
               .having(is_active=False))
        create(Builder('organization')
               .having(former_contact_id=445566)
               .named(u'AAA Design'))

    @browsing
    def test_lists_only_active_organizations_by_default(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-organizations')

        self.assertEquals(
            [[u'Name', 'Active', 'Former contact ID'],
             [u'AAA Design', 'Yes', '445566'],
             [u'Meier AG', 'Yes', '112233']],
            browser.css('.listing').first.lists())

        self.assertEquals(['Active'],
                          browser.css('.state_filters .active').text)

    @browsing
    def test_statefilters_are_available(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-organizations')

        self.assertEquals(['label_tabbedview_filter_all', 'Active'],
                          browser.css('.state_filters a').text)

    @browsing
    def test_includes_inactive_organizations_with_the_all_filter(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-organizations',
            data={'organization_state_filter': 'filter_all'})

        self.assertEquals(
            [[u'Name', 'Active', 'Former contact ID'],
             [u'AAA Design', 'Yes', '445566'],
             [u'Meier AG', 'Yes', '112233'],
             [u'M\xfcller', 'No', '']],
            browser.css('.listing').first.lists())

    @browsing
    def test_name_is_linked_to_organization_view(self, browser):
        browser.login().open(
            self.contactfolder, view='tabbedview_view-organizations')

        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/contact-1/view',
            browser.find(u'Meier AG').get('href'))

    @browsing
    def test_filtering_on_name(self, browser):
        browser.login().open(
            self.contactfolder,
            view='tabbedview_view-organizations',
            data={'searchable_text': 'Design'})

        self.assertEquals(
            [[u'Name', 'Active', 'Former contact ID'],
             [u'AAA Design', 'Yes', '445566']],
            browser.css('.listing').first.lists())
