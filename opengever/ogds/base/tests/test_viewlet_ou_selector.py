from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import select_current_org_unit
from plone.app.testing import TEST_USER_ID


class TestOrgUnitSelectorViewlet(FunctionalTestCase):

    def setUp(self):
        super(TestOrgUnitSelectorViewlet, self).setUp()
        self.client4 = create_client('client4', title='Client 4',
                                     public_url='http://nohost/plone')
        self.client3 = create_client('client3', title='Client 3')
        self.client1 = create_client('client1', title='Client 1')
        self.client2 = create_client('client2', title='Client 2')

        create_ogds_user(
            TEST_USER_ID,
            assigned_client=[self.client1, self.client3, self.client4])

        self.repo_root = create(Builder('repository_root'))

    @browsing
    def test_units_are_sorted_alphabetically(self, browser):
        browser.login().open(self.repo_root)
        units = browser.css('.orgunitMenuContent li')

        self.assertEquals(
            ['Client 3', 'Client 4'], units.text)

    @browsing
    def test_first_unit_is_marked_as_active_per_default(self, browser):
        browser.login().open(self.repo_root)

        active_unit = browser.css('.orgunitMenu dt a')
        self.assertEquals(
            ['Client 1'], active_unit.text)

    @browsing
    def test_list_all_assigned_units_except_current_one(self, browser):
        browser.login().open(self.repo_root)
        units = browser.css('.orgunitMenuContent li')

        self.assertEquals(
            ['Client 3', 'Client 4'], units.text)

    @browsing
    def test_selecting_a_unit_changes_active_unit(self, browser):
        browser.login().open(self.repo_root)

        browser.css('.orgunitMenuContent a')[1].click()

        active_unit = browser.css('.orgunitMenu dt a')
        self.assertEquals(
            ['Client 4'], active_unit.text)
