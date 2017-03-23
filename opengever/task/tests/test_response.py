from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from zExceptions import Unauthorized
from zope.component import getMultiAdapter


class TestTaskCommentResponseAddFormView(FunctionalTestCase):

    @browsing
    def test_add_task_comment_response_view_is_available(self, browser):
        task = create(Builder('task').titled('Task 1'))

        browser.login().visit(task, view="addtaskcommentresponse")
        self.assertEqual(
            'Add Comment',
            browser.css('.documentFirstHeading').first.text)

    @browsing
    def test_default_task_response_form_fields(self, browser):
        task = create(Builder('task').titled('Task 1'))

        browser.login().visit(task, view="addtaskcommentresponse")
        labels = browser.css('#content-core label').text

        # remove empty labels.
        labels = filter(lambda item: item, labels)

        self.assertEqual(['Response'], labels)

    @browsing
    def test_add_related_response_object_after_commenting(self, browser):
        task = create(Builder('task').titled('Task 1'))

        browser.login().visit(task, view="addtaskcommentresponse")
        browser.fill({'Response': 'I am a comment'}).find('Save').click()
        browser.open(task, view='tabbedview_view-overview')

        self.assertEqual(
            'Commented by Test User (test_user_1_)',
            self.get_latest_answer(browser))

    @browsing
    def test_click_on_comment_button_redirects_to_add_comment_view(self, browser):
        task = create(Builder('task').titled('Task 1'))
        browser.login().open(task, view='tabbedview_view-overview')

        browser.css('.taskCommented').first.click()

        self.assertEqual(
            '{}/@@addtaskcommentresponse'.format(task.absolute_url()),
            browser.url)

    @browsing
    def test_do_not_show_comment_button_if_dossier_is_closed(self, browser):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))

        task = create(Builder('task').titled('Task 1').within(dossier))
        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEqual(0, len(browser.css('.taskCommented')))

    def test_protect_addcommenttaskresponse_view_if_containing_dossier_is_closed(self):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))

        task = create(Builder('task').titled('Task 1').within(dossier))
        view = getMultiAdapter((task, self.request), name='addtaskcommentresponse')

        with self.assertRaises(Unauthorized):
            view()

    def test_protect_addcommenttaskresponse_view_if_user_has_no_add_permission(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier'))
        task = create(Builder('task').titled('Task 1').within(dossier))

        self.login('hugo.boss')
        view = getMultiAdapter((task, self.request), name='addtaskcommentresponse')

        with self.assertRaises(Unauthorized):
            view()

    def get_latest_answer(self, browser):
        latest_answer = browser.css('div.answers .answer').first
        return latest_answer.css('h3').text[0]
