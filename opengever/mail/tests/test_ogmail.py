from ftw.builder import Builder
from ftw.builder import create
from opengever.mail.mail import IOGMailMarker
from opengever.testing import FunctionalTestCase
import os


MAIL_DATA = open(
    os.path.join(os.path.dirname(__file__), 'mail.txt'), 'r').read()


class TestOGMailAddition(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestOGMailAddition, self).setUp()
        self.grant('Contributor', 'Editor', 'Member', 'Manager')

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

    def test_mail_behavior(self):
        mail = create(Builder("mail").with_message(MAIL_DATA))

        self.browser.open('%s/edit' % mail.absolute_url())
        self.browser.getControl(
            name='form.widgets.IOGMail.title').value = 'hanspeter'
        self.browser.getControl(name='form.buttons.save').click()

        self.assertEquals(u'hanspeter', mail.title)
        self.assertEquals('hanspeter', mail.Title())

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
