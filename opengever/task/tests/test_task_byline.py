from ftw.testbrowser import browsing
from opengever.base.tests.byline_base_test import TestBylineBase


class TestTaskByline(TestBylineBase):

    @browsing
    def test_task_byline_responsible_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task)

        responsible = self.get_byline_value_by_label('by:')
        self.assertEquals(u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                          responsible.text)

    @browsing
    def test_dossier_byline_responsible_is_linked_to_user_details(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task)

        responsible = self.get_byline_value_by_label('by:')
        self.assertEqual('http://nohost/plone/kontakte/user-kathi.barfuss/view',
                         responsible.get('href'))

    @browsing
    def test_task_byline_state_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task)

        state = self.get_byline_value_by_label('State:')
        self.assertEquals('task-state-in-progress', state.text)

    @browsing
    def test_task_byline_start_date_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task)

        start_date = self.get_byline_value_by_label('created:')
        self.assertEquals('Aug 31, 2016 06:01 PM', start_date.text)

    @browsing
    def test_task_byline_modification_date_display(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task)

        start_date = self.get_byline_value_by_label('last modified:')
        self.assertEquals('Aug 31, 2016 06:05 PM', start_date.text)

    @browsing
    def test_dossier_byline_sequence_number_display_is_prefixed_with_admin_unit_abbreviation(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task)

        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('Client1 1', seq_number.text)

    @browsing
    def test_is_private_attribute_is_displayed_in_byline_for_private_task(self, browser):
        self.login(self.regular_user, browser=browser)

        self.task.is_private = True
        browser.open(self.task)

        is_private = self.get_byline_value_by_label('Private:')
        self.assertEquals('Yes', is_private.text)

    @browsing
    def test_is_private_attribute_is_not_displayed_in_byline_for_default_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task)

        self.assertIsNone(self.get_byline_value_by_label('Private:'))
