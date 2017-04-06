from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import FunctionalTestCase
from zExceptions import Unauthorized
from zope.component import getMultiAdapter


class TestTaskCommentResponseAddFormView(FunctionalTestCase):

    @browsing
    def test_add_task_comment_response_view_is_available(self, browser):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))

        browser.login().visit(task, view="addcommentresponse")
        self.assertEqual(
            'Add Comment',
            browser.css('.documentFirstHeading').first.text)

    @browsing
    def test_default_task_response_form_fields(self, browser):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))

        browser.login().visit(task, view="addcommentresponse")
        labels = browser.css('#content-core label').text

        # remove empty labels.
        labels = filter(lambda item: item, labels)

        self.assertEqual(['Response'], labels)

    @browsing
    def test_add_related_response_object_after_commenting(self, browser):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))

        browser.login().visit(task, view="addcommentresponse")
        browser.fill({'Response': 'I am a comment'}).find('Save').click()
        browser.open(task, view='tabbedview_view-overview')

        self.assertEqual(
            'Commented by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_text_field_is_required_for_comments(self, browser):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task').within(dossier))

        browser.login().visit(task, view="addcommentresponse")
        browser.find('Save').click()

        self.assertEqual(
            ['There were some errors.'],
            statusmessages.error_messages())

    @browsing
    def test_click_on_comment_button_redirects_to_add_comment_view(self, browser):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))
        browser.login().open(task, view='tabbedview_view-overview')

        browser.css('.taskCommented').first.click()

        self.assertEqual(
            '{}/@@addcommentresponse'.format(task.absolute_url()),
            browser.url)

    @browsing
    def test_do_not_show_comment_button_if_dossier_is_closed(self, browser):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))

        task = create(Builder('task').titled('Task 1').within(dossier))
        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEqual(0, len(browser.css('.taskCommented')))

    @browsing
    def test_Manager_can_access_addcommentresponse_view_on_open_dossier(self, browser):
        self.grant('Manager')
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))

        self.assertEqual(
            '{}/addcommentresponse'.format(task.absolute_url()),
            browser.login().open(task, view='addcommentresponse').url)

    @browsing
    def test_Adminstrator_can_access_addcommentresponse_view_on_open_dossier(self, browser):
        self.grant('Adminstrator')
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))

        self.assertEqual(
            '{}/addcommentresponse'.format(task.absolute_url()),
            browser.login().open(task, view='addcommentresponse').url)

    @browsing
    def test_Contributor_can_access_addcommentresponse_view_on_open_dossier(self, browser):
        self.grant('Contributor')
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))

        self.assertEqual(
            '{}/addcommentresponse'.format(task.absolute_url()),
            browser.login().open(task, view='addcommentresponse').url)

    @browsing
    def test_Editor_can_access_addcommentresponse_view_on_open_dossier(self, browser):
        self.grant('Editor')
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))

        self.assertEqual(
            '{}/addcommentresponse'.format(task.absolute_url()),
            browser.login().open(task, view='addcommentresponse').url)

    @browsing
    def test_Reader_can_not_access_addcommentresponse_view_on_open_dossier(self, browser):
        self.grant('Reader')
        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))

        self.assertEqual(
            '{}/addcommentresponse'.format(task.absolute_url()),
            browser.login().open(task, view='addcommentresponse').url)

    @browsing
    def test_Manager_can_not_access_addcommentresponse_view_on_closed_dossier(self, browser):
        self.grant('Manager')
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))

        task = create(Builder('task').titled('Task 1').within(dossier))

        with self.assertRaises(Unauthorized):
            browser.login().open(task, view='addcommentresponse')

    @browsing
    def test_Adminstrator_can_not_access_addcommentresponse_view_on_closed_dossier(self, browser):
        self.grant('Adminstrator')
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))

        task = create(Builder('task').titled('Task 1').within(dossier))

        with self.assertRaises(Unauthorized):
            browser.login().open(task, view='addcommentresponse')

    @browsing
    def test_Contributor_can_not_access_addcommentresponse_view_on_closed_dossier(self, browser):
        self.grant('Contributor')
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))

        task = create(Builder('task').titled('Task 1').within(dossier))

        with self.assertRaises(Unauthorized):
            browser.login().open(task, view='addcommentresponse')

    @browsing
    def test_Editor_can_not_access_addcommentresponse_view_on_closed_dossier(self, browser):
        self.grant('Editor')
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))

        task = create(Builder('task').titled('Task 1').within(dossier))

        with self.assertRaises(Unauthorized):
            browser.login().open(task, view='addcommentresponse')

    @browsing
    def test_Reader_can_not_access_addcommentresponse_view_on_closed_dossier(self, browser):
        self.grant('Reader')
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))

        task = create(Builder('task').titled('Task 1').within(dossier))

        with self.assertRaises(Unauthorized):
            browser.login().open(task, view='addcommentresponse')

    def get_latest_answer(self, browser):
        latest_answer = browser.css('div.answers .answer').first
        return latest_answer.css('h3').text[0]
