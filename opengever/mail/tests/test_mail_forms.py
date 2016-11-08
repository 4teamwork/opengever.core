from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME


class TestMailForms(FunctionalTestCase):

    def setUp(self):
        super(TestMailForms, self).setUp()
        login(self.portal, TEST_USER_NAME)
        self.mail = create(Builder("mail"))

    @browsing
    def test_edit_form_does_not_contain_change_note(self, browser):
        browser.login().open(self.mail, view='edit')

        inputs = [input.name for input in browser.forms.get('form').inputs]
        self.assertNotIn('form.widgets.IVersionable.changeNote', inputs)

    @browsing
    def test_add_form_does_not_contain_change_note(self, browser):
        browser.login().open(self.portal, view='++add++ftw.mail.mail')

        inputs = [input.name for input in browser.forms.get('form').inputs]
        self.assertNotIn('form.widgets.IVersionable.changeNote', inputs)
