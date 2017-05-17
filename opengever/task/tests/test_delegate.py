from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
import datetime


class TestDelegateTaskForm(FunctionalTestCase):

    @browsing
    def test_delegate(self, browser):
        task = create(Builder('task')
                      .titled('A Task')
                      .having(issuer=TEST_USER_ID,
                              deadline=datetime.date(2013, 1, 1))
                      .in_state('task-state-in-progress'))

        # pre-fill responsibles
        selected_user = '{}:{}'.format(self.org_unit.id(), self.user.userid)
        browser.login().visit(task, view='delegate_recipients')

        form = browser.find_form_by_field('Responsibles')
        form.find_widget('Responsibles').fill(selected_user)

        browser.css('#form-buttons-save').first.click()  # can't use submit()

        browser.fill({'Issuer': self.user.userid})
        browser.css('#form-buttons-save').first.click()  # can't use submit()
