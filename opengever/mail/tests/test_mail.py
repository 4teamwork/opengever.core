from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestMail(IntegrationTestCase):

    @browsing
    def test_regular_user_can_add_new_keywords_in_mail(self, browser):
        self.login(self.regular_user, browser)

        browser.visit(self.mail_eml, view='@@edit')
        keywords = browser.find_field_by_text(u'Keywords')
        self.assertTupleEqual(tuple(), tuple(keywords.value))

        new = browser.css('#' + keywords.attrib['id'] + '_new').first
        new.text = u'NewItem1\nNew Item 2\nN\xf6i 3'
        browser.find_button_by_label('Save').click()

        browser.visit(self.mail_eml, view='edit')
        keywords = browser.find_field_by_text(u'Keywords')
        self.assertTupleEqual(('New Item 2', 'NewItem1', 'N=C3=B6i 3'),
                              tuple(keywords.value))
