from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.caching.interfaces import IETagValue
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter


class TestOrgUnitSelectorViewletIsAvailable(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestOrgUnitSelectorViewletIsAvailable, self).setUp()

        test_user = create(Builder('ogds_user').id(TEST_USER_ID))

        self.admin_unit = create(Builder('admin_unit')
                                 .as_current_admin_unit()
                                 .having(public_url='http://nohost/plone'))

        self.org_unit = create(Builder('org_unit')
                               .id(u'unit 1')
                               .as_current_org_unit()
                               .having(title=u'Unit 1',
                                       admin_unit=self.admin_unit)
                               .assign_users([test_user]))

        self.repo_root = create(Builder('repository_root'))

    @browsing
    def test_org_unit_selector_not_visible_for_lone_org_unit(self, browser):
        browser.login().open(self.repo_root)
        self.assertEqual([], browser.css('#portal-orgunit-selector'))

    @browsing
    def test_org_unit_selector_visible_for_multiple_org_units(self, browser):
        create(Builder('org_unit')
               .id(u'unit 2')
               .as_current_org_unit()
               .having(title=u'Unit 2', admin_unit=self.admin_unit))

        browser.login().open(self.repo_root)
        self.assertEqual(1, len(browser.css('#portal-orgunit-selector')))


class TestOrgUnitSelectorViewlet(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestOrgUnitSelectorViewlet, self).setUp()

        test_user = create(Builder('ogds_user').id(TEST_USER_ID))

        self.admin_unit = create(Builder('admin_unit')
                                 .as_current_admin_unit()
                                 .having(public_url='http://nohost/plone'))

        self.admin_unit_2 = create(Builder('admin_unit')
                                   .id('unit2')
                                   .having(public_url='http://nohost/plone'))

        self.org_unit4 = create(Builder('org_unit')
                                .id(u'client4')
                                .having(title=u'Client 4',
                                        admin_unit=self.admin_unit)
                                .assign_users([test_user]))
        self.org_unit3 = create(Builder('org_unit')
                                .id(u'client3')
                                .having(title=u'Client 3',
                                        admin_unit=self.admin_unit)
                                .assign_users([test_user]))
        self.org_unit1 = create(Builder('org_unit')
                                .id(u'client1')
                                .as_current_org_unit()
                                .having(title=u'Client 1',
                                        admin_unit=self.admin_unit)
                                .assign_users([test_user]))
        self.org_unit2 = create(Builder('org_unit')
                                .id(u'client2')
                                .having(title=u'Client 2',
                                        admin_unit=self.admin_unit))

        self.org_unit5 = create(Builder('org_unit')
                                .id(u'client5')
                                .having(title=u'Client 5',
                                        admin_unit=self.admin_unit))

        self.repo_root = create(Builder('repository_root'))

    @browsing
    def test_units_are_sorted_alphabetically(self, browser):
        browser.login().open(self.repo_root)
        units = browser.css('.orgunitMenuContent li')

        self.assertEquals(
            ['Client 1', 'Client 3', 'Client 4'], units.text)

    @browsing
    def test_first_unit_is_marked_as_active_per_default(self, browser):
        browser.login().open(self.repo_root)

        active_unit = browser.css('.orgunitMenu dt a')
        self.assertEquals(
            ['Client 1'], active_unit.text)

    @browsing
    def test_list_all_assigned_units(self, browser):
        browser.login().open(self.repo_root)
        units = browser.css('.orgunitMenuContent li')

        self.assertEquals(
            ['Client 1', 'Client 3', 'Client 4'], units.text)

    @browsing
    def test_list_only_current_admin_units_org_units(self, browser):
        browser.login().open(self.repo_root)
        units = browser.css('.orgunitMenuContent li')

        self.assertEquals(
            ['Client 1', 'Client 3', 'Client 4'], units.text)

    @browsing
    def test_list_only_enabled_org_units(self, browser):
        self.org_unit3.enabled = False
        browser.login().open(self.repo_root)
        units = browser.css('.orgunitMenuContent li')

        self.assertEquals(
            ['Client 1', 'Client 4'], units.text)

    @browsing
    def test_list_only_visible_org_units(self, browser):
        self.org_unit3.hidden = True
        browser.login().open(self.repo_root)
        units = browser.css('.orgunitMenuContent li')

        self.assertEquals(
            ['Client 1', 'Client 4'], units.text)

    @browsing
    def test_active_unit_is_not_linked(self, browser):
        browser.login().open(self.repo_root)
        units = browser.css('.orgunitMenuContent li span')

        self.assertEquals(['Client 1'], units.text)

    @browsing
    def test_active_unit_has_class_active(self, browser):
        browser.login().open(self.repo_root)
        units = browser.css('.orgunitMenuContent li span.active')

        self.assertEquals(['Client 1'], units.text)

    @browsing
    def test_selecting_a_unit_changes_active_unit(self, browser):
        browser.login().open(self.repo_root)
        browser.css('.orgunitMenuContent a')[1].click()

        active_unit = browser.css('.orgunitMenu dt a')
        self.assertEquals(
            ['Client 4'], active_unit.text)

    def test_etag_value_returns_current_org_unit_id(self):
        view = self.repo_root.unrestrictedTraverse('@@view')
        self.assertEquals('client1', self.get_etag_value_for(view))

        self.portal.REQUEST['unit_id'] = 'client4'
        self.portal.unrestrictedTraverse('change_org_unit')()

        view = self.repo_root.unrestrictedTraverse('@@view')
        self.assertEquals('client4', self.get_etag_value_for(view))

    def get_etag_value_for(self, view):
        adapter = getMultiAdapter((view, self.request),
                                  IETagValue,
                                  name='ouselector')
        return adapter()
