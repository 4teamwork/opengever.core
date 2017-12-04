from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.ogds.base.utils import get_current_org_unit
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
import datetime


class TestDelegateTaskToInbox(IntegrationTestCase):

    @browsing
    def test_delegate_to_inbox(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.task,
                     view='@@task_transition_controller',
                     data={'transition': 'task-transition-delegate'})

        form = browser.find_form_by_field('Responsibles')
        form.find_widget('Responsibles').fill(
            ['inbox:{}'.format(get_current_org_unit().id())])
        browser.css('#form-buttons-save').first.click()  # can't use submit()

        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(self.dossier_responsible.getId())

        browser.css('#form-buttons-save').first.click()  # can't use submit()

        self.assertEqual(['1 subtasks were create.'],
                         statusmessages.info_messages())


class TestDelegateTaskForm(FunctionalTestCase):

    @browsing
    def test_delegate(self, browser):
        task = create(Builder('task')
                      .titled(u'A Task')
                      .having(issuer=TEST_USER_ID,
                              deadline=datetime.date(2013, 1, 1))
                      .in_state('task-state-in-progress'))

        # pre-fill responsibles
        selected_user = '{}:{}'.format(self.org_unit.id(), self.user.userid)
        browser.login().visit(task, view='delegate_recipients')

        form = browser.find_form_by_field('Responsibles')
        form.find_widget('Responsibles').fill(selected_user)

        browser.css('#form-buttons-save').first.click()  # can't use submit()

        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(self.user.userid)

        browser.css('#form-buttons-save').first.click()  # can't use submit()
