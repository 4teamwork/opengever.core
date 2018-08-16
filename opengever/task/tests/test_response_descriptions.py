from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.task.adapters import IResponseContainer
from opengever.task.adapters import IResponseContainer
from opengever.task.adapters import Response
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
import transaction


class TestResponseDescriptions(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestResponseDescriptions, self).setUp()
        self.admin_unit = create(
            Builder('fixture')
            .with_admin_unit(public_url='http://plone'))

        self.user = create(Builder('ogds_user')
                           .having(userid=TEST_USER_ID,
                                   firstname=u'Hans',
                                   lastname=u'M\xfcller'))

        self.other_user = create(Builder('ogds_user')
                                 .having(userid='other_user',
                                         firstname=u'J\xf6rg',
                                         lastname='Steiner'))

        create(Builder('org_unit')
               .as_current_org_unit()
               .id('org-unit-1')
               .having(title=u'Amt f\xfcr Umwelt', admin_unit=self.admin_unit)
               .assign_users([self.user, self.other_user]))

        # TODO: Use non-ASCII characters in dossier title as well, but
        # currently og.globalindex.model.task.Task.sync_with() can't
        # handle it correctly
        self.dossier = create(Builder('dossier').titled(u'Dossier'))

        self.task = create(Builder("task")
                           .within(self.dossier)
                           .titled(u'Aufgabe f\xfcr Hans')
                           .having(text=u'Text f\xfcr Aufgabe',
                                   task_type='comment',
                                   deadline=date(2010, 1, 1),
                                   issuer=TEST_USER_ID,
                                   responsible=TEST_USER_ID,
                                   responsible_client='org-unit-1'))

    def get_latest_answer(self, browser):
        latest_answer = browser.css('div.answers .answer').first
        return latest_answer.css('h3').text[0]

    def click_task_button(self, browser, button_class, save_and_reload=True):
        """Visits the overview view on `self.task`, clicks the button
        identified by the CSS class `button_class`, and, if `save_and_reload`
        is True, saves the form and reloads the overview view.
        """
        # browser.open(self.task, view='tabbedview_view-overview')
        self.visit_overview(browser)
        button = browser.css('.{}'.format(button_class)).first
        button.click()
        if save_and_reload:
            browser.forms.get('form').save()
            self.visit_overview(browser)

    def visit_overview(self, browser, task=None):
        if task is None:
            task = self.task
        browser.open(self.task, view='tabbedview_view-overview')

    @browsing
    def test_reactivating_creates_response(self, browser):
        browser.login()

        # Cancel task first
        self.click_task_button(browser, 'cancelled')

        # Reactivate task
        self.click_task_button(browser, 'reactivate')

        self.assertEqual(
            u'Reactivate by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_rejecting_task_creates_response(self, browser):
        browser.login()

        # Reject task
        # (CSS class is .refuse even though the transition is named 'reject')
        self.click_task_button(browser, 'refuse')

        self.assertEqual(
            u'Rejected by M\xfcller Hans (test_user_1_). Task assigned to responsible M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_reject_response_for_older_tasks(self, browser):
        """The responsible gets changed since the release 2018.4, before
        rejecting a task was only a status change, so we need to test for
        another message.
        """

        browser.login()

        # Reject task
        # (CSS class is .refuse even though the transition is named 'reject')
        self.click_task_button(browser, 'refuse')

        # Manually remove responsible change information from the response
        # to fake an old task situation.
        response = IResponseContainer(self.task)[-1]
        response.changes = [
            change for change in response.changes if change['id'] != 'responsible']
        transaction.commit()

        browser.reload()
        self.assertEqual(u'Rejected by M\xfcller Hans (test_user_1_).',
                         self.get_latest_answer(browser))

    @browsing
    def test_resolving_creates_response(self, browser):
        browser.login()

        # Resolve task
        self.click_task_button(browser, 'complete')

        self.assertEqual(
            u'Resolved by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_closing_creates_response(self, browser):
        browser.login()

        # Resolve task
        self.click_task_button(browser, 'close')

        self.assertEqual(
            u'Closed by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_cancelling_creates_response(self, browser):
        browser.login()

        # Cancel task
        self.click_task_button(browser, 'cancelled')

        self.assertEqual(
            u'Cancelled by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_accepting_creates_response(self, browser):
        browser.login()
        # Accept task
        self.click_task_button(browser, 'accept')

        self.assertEqual(
            u'Accepted by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_reopening_creates_response(self, browser):
        browser.login()

        # Refuse task first
        self.click_task_button(browser, 'refuse')

        # Reopen task
        self.click_task_button(browser, 'reopen')

        self.assertEqual(
            u'Reopened by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_revising_creates_response(self, browser):
        browser.login()

        # Complete task first
        self.click_task_button(browser, 'complete')

        # Revise task
        self.click_task_button(browser, 'revise')

        self.assertEqual(
            u'Revised by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_reassigning_creates_response(self, browser):
        browser.login()

        # Reassign task
        self.click_task_button(browser, 'reassign', save_and_reload=False)

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('org-unit-1:other_user')

        browser.find('Assign').click()
        self.visit_overview(browser)

        self.assertEqual(
            u'Reassigned from M\xfcller Hans (test_user_1_) to Steiner '
            u'J\xf6rg (other_user) by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_modifying_deadline_creates_response(self, browser):
        browser.login()

        # Modify deadline
        self.click_task_button(browser, 'modifyDeadline',
                               save_and_reload=False)
        browser.fill({'New Deadline': '07.07.2015'})
        browser.forms.get('form').save()
        self.visit_overview(browser)

        self.assertEqual(
            u'Deadline modified from 01.01.2010 to 07.07.2015 '
            u'by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_delegating_task_creates_no_response(self, browser):
        browser.login()

        # Accept task first
        self.click_task_button(browser, 'accept')

        # Delegate task
        #
        # Step 1 - Select new responsible(s)
        self.click_task_button(browser, 'delegate', save_and_reload=False)
        form = browser.find_form_by_field('Responsibles')
        form.find_widget('Responsibles').fill('org-unit-1:test_user_1_')

        browser.find('Continue').click()

        # Step 2 - Update metadata of new subtask
        browser.fill({'Title': 'My delegated subtask'})
        browser.forms.get('form').save()
        self.visit_overview(browser)

        # Delegation doesn't create a response (yet), but adding subtask does
        self.assertEqual(
            u'Subtask My delegated subtask (M\xfcller Hans (test_user_1_)) '
            u'added by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_adding_subtask_creates_response(self, browser):
        create(Builder('task')
               .titled(u'My Subtask')
               .within(self.task))

        browser.login()
        self.visit_overview(browser)

        self.assertEqual(
            u'Subtask My Subtask (M\xfcller Hans (test_user_1_)) added by '
            u'M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_adding_document_creates_response(self, browser):
        create(Builder('document')
               .titled(u'Sanierung B\xe4rengraben.docx')
               .within(self.task))

        browser.login()
        self.visit_overview(browser)

        self.assertEqual(
            u'Document Sanierung B\xe4rengraben.docx added by '
            u'M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_adding_mail_creates_response(self, browser):
        create(Builder('mail')
               .with_dummy_message()
               .within(self.task))

        browser.login()
        self.visit_overview(browser)

        self.assertEqual(
            u'Document [No Subject] added by M\xfcller Hans (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_null_fallback(self, browser):
        # add null response
        null_response = Response(None)
        IResponseContainer(self.task).add(null_response)
        transaction.commit()

        browser.login()
        self.visit_overview(browser)

        self.assertEqual('answer null-transition',
                         browser.css('div.answer')[0].get('class'))
        self.assertEqual('', self.get_latest_answer(browser))


    # TODO:
    # - Test assigning forwarding to dossier
    # - Test refusing a forwarding
