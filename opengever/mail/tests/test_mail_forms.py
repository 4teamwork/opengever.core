from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME


class TestMailForms(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestMailForms, self).setUp()
        self.grant('Manager')
        login(self.portal, TEST_USER_NAME)
        self.mail = create(Builder("mail"))

    def test_edit_form_does_not_contain_change_note(self):
        self.browser.open('%s/edit' % self.mail.absolute_url())

        # the changeNote field from IVersionable should not show up
        self.assertPageContainsNot('form.widgets.IVersionable.changeNote')

    def test_add_form_does_not_contain_change_note(self):
        self.browser.open('%s/++add++ftw.mail.mail' % self.portal.absolute_url())

        # the changeNote field from IVersionable should not show up
        self.assertPageContainsNot('form.widgets.IVersionable.changeNote')
