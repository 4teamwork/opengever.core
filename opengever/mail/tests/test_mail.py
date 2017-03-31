from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestMail(FunctionalTestCase):

    @browsing
    def test_regular_user_can_add_new_keywords_in_mail(self, browser):
        dossier = create(Builder('dossier'))
        mail = create(Builder('mail').within(dossier))

        self.grant('Reader', 'Contributor', 'Editor')

        browser.login().visit(mail, view='@@edit')

        keywords = browser.find_field_by_text(u'Keywords')
        new = browser.css('#' + keywords.attrib['id'] + '_new').first
        new.text = u'NewItem1\nNew Item 2\nN\xf6i 3'
        browser.find_button_by_label('Save').click()

        browser.visit(mail, view='edit')
        keywords = browser.find_field_by_text(u'Keywords')
        self.assertTupleEqual(('New Item 2', 'NewItem1', 'N=C3=B6i 3'),
                              tuple(keywords.value))
