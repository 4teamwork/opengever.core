from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


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

        self.assertEqual(['Response', 'Related Items'], labels)
