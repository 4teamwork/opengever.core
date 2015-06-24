from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.mail.mail import IOGMailMarker
from opengever.mail.tests import MAIL_DATA
from opengever.testing import FunctionalTestCase
from plone import api


class TestOGMailAddition(FunctionalTestCase):

    def test_og_mail_behavior(self):
        mail = create(Builder("mail"))
        self.assertTrue(
            IOGMailMarker.providedBy(mail),
            'ftw mail obj does not provide the OGMail behavior interface.')

    def test_title_accessor(self):
        mail = create(Builder("mail"))
        self.assertEquals(u'[No Subject]', mail.title)
        self.assertEquals('[No Subject]', mail.Title())

        mail = create(Builder("mail").with_message(MAIL_DATA))

        self.assertEquals(u'Die B\xfcrgschaft', mail.title)
        self.assertEquals('Die B\xc3\xbcrgschaft', mail.Title())

    @browsing
    def test_mail_behavior(self, browser):
        mail = create(Builder("mail").with_message(MAIL_DATA))

        browser.login().open(mail, view='edit')
        browser.fill({'Title': u'hanspeter'}).submit()

        self.assertEquals(u'hanspeter', mail.title)
        self.assertEquals('hanspeter', mail.Title())

    def test_copy_mail_preserves_author(self):
        dossier_1 = create(Builder('dossier'))
        dossier_2 = create(Builder('dossier'))
        mail = create(Builder('mail')
                      .within(dossier_1)
                      .with_message(MAIL_DATA)
                      .having(document_author='Hanspeter'))

        self.assertEqual('Hanspeter', mail.document_author)

        copy = api.content.copy(source=mail, target=dossier_2)
        self.assertEqual('Hanspeter', copy.document_author)

    def test_mail_is_never_checked_out(self):
        mail = create(Builder("mail").with_dummy_message())

        self.assertEquals(None, mail.checked_out_by())
        self.assertEquals(False, mail.is_checked_out())

    def test_mail_has_no_related_items(self):
        mail = create(Builder("mail").with_dummy_message())

        self.assertEquals([], mail.related_items())

    def test_is_removed(self):
        mail_a = create(Builder('mail'))
        mail_b = create(Builder('mail').removed())

        self.assertFalse(mail_a.is_removed)
        self.assertTrue(mail_b.is_removed)
