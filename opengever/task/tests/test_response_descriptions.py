from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestResponseDescriptions(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestResponseDescriptions, self).setUp()
        self.admin_unit = create(
            Builder('fixture')
            .with_admin_unit(public_url='http://plone'))

        self.user = create(Builder('ogds_user')
                           .having(userid=TEST_USER_ID,
                                   firstname='User',
                                   lastname='Test'))

        self.other_user = create(Builder('ogds_user')
                                 .having(userid='other_user',
                                         firstname='Other',
                                         lastname='User'))

        create(Builder('org_unit')
               .as_current_org_unit()
               .id('client1')
               .having(title="Organization 1", admin_unit=self.admin_unit)
               .assign_users([self.user, self.other_user]))

        self.dossier = create(Builder('dossier').titled(u'Dossier'))

        self.task = create(Builder("task")
                           .within(self.dossier)
                           .titled(u'Aufgabe')
                           .having(text='Text blabla',
                                   task_type='comment',
                                   deadline=datetime(2010, 1, 1),
                                   issuer=TEST_USER_ID,
                                   responsible=TEST_USER_ID,
                                   responsible_client='client1'))

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
        button = browser.css('.button.{}'.format(button_class)).first
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
            'Reactivate by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_rejecting_task_creates_response(self, browser):
        browser.login()

        # Reject task
        # (CSS class is .refuse even though the transition is named 'reject')
        self.click_task_button(browser, 'refuse')

        self.assertEqual(
            'Rejected by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_resolving_creates_response(self, browser):
        browser.login()

        # Resolve task
        self.click_task_button(browser, 'complete')

        self.assertEqual(
            'Resolved by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_closing_creates_response(self, browser):
        browser.login()

        # Resolve task
        self.click_task_button(browser, 'close')

        self.assertEqual(
            'Closed by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_cancelling_creates_response(self, browser):
        browser.login()

        # Cancel task
        self.click_task_button(browser, 'cancelled')

        self.assertEqual(
            'Cancelled by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_accepting_creates_response(self, browser):
        browser.login()
        # Accept task
        self.click_task_button(browser, 'accept')

        self.assertEqual(
            'Accepted by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_reopening_creates_response(self, browser):
        browser.login()

        # Refuse task first
        self.click_task_button(browser, 'refuse')

        # Reopen task
        self.click_task_button(browser, 'reopen')

        self.assertEqual(
            'Reopened by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_revising_creates_response(self, browser):
        browser.login()

        # Complete task first
        self.click_task_button(browser, 'complete')

        # Revise task
        self.click_task_button(browser, 'revise')

        self.assertEqual(
            'Revised by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_reassigning_creates_response(self, browser):
        browser.login()

        # Reassign task
        self.click_task_button(browser, 'reassign', save_and_reload=False)

        user, = browser.find('Responsible').query('other_user')
        browser.fill({'Responsible': user[0]})
        browser.find('Assign').click()
        self.visit_overview(browser)

        self.assertEqual(
            'Reassigned from Test User (test_user_1_) to User Other '
            '(other_user) by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_modifying_deadline_creates_response(self, browser):
        browser.login()

        # Modify deadline
        self.click_task_button(browser, 'modifyDeadline',
                               save_and_reload=False)
        browser.fill({'New Deadline': '07/07/15'})
        browser.forms.get('form').save()
        self.visit_overview(browser)

        self.assertEqual(
            'Deadline modified from 01.01.2010 to 07.07.2015 '
            'by Test User (test_user_1_)',
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
        user, = browser.find('Responsibles').query('test_user')
        browser.fill({'Responsibles': user[0]})
        browser.find('Continue').click()

        # Step 2 - Update metadata of new subtask
        browser.fill({'Title': 'My delegated subtask'})
        browser.forms.get('form').save()
        self.visit_overview(browser)

        # Delegation doesn't create a response (yet), but adding subtask does
        self.assertEqual(
            'Subtask My delegated subtask (Test User (test_user_1_)) added '
            'by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_adding_subtask_creates_response(self, browser):
        create(Builder('task')
               .titled(u'My Subtask')
               .within(self.task))

        browser.login()
        self.visit_overview(browser)

        self.assertEqual(
            'Subtask My Subtask (Test User (test_user_1_)) added by '
            'Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_adding_document_creates_response(self, browser):
        create(Builder('document')
               .titled(u'Ein Dokument.docx')
               .within(self.task))

        browser.login()
        self.visit_overview(browser)

        self.assertEqual(
            'Document Ein Dokument.docx added by '
            'Test User (test_user_1_)',
            self.get_latest_answer(browser))

    # TODO:
    # - Test assigning forwarding to dossier
    # - Test refusing a forwarding
