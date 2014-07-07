from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
import datetime


class TestDelegateTaskForm(FunctionalTestCase):

    def setUp(self):
        super(TestDelegateTaskForm, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    @browsing
    def test_delegate(self, browser):
        task = create(Builder('task')
                      .titled('A Task')
                      .having(issuer=TEST_USER_ID,
                              deadline=datetime.date(2013, 1, 1))
                      .in_state('task-state-in-progress'))

        # pre-fill responsibles
        selected_user = '{}:{}'.format(self.org_unit.id(), self.user.userid)
        url = "{}/@@delegate_recipients?form.widgets.responsibles={}".format(
            task.absolute_url(), selected_user)
        browser.login().open(url)
        browser.css('#form-buttons-save').first.click()  # can't use submit()

        browser.fill({'Issuer': self.user.userid})
        browser.css('#form-buttons-save').first.click()  # can't use submit()
