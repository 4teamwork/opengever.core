from Testing.makerequest import makerequest
from opengever.mail.mail import IOGMailMarker, IOGMail
from opengever.testing import FunctionalTestCase
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from zope.app.component.hooks import setSite
import os
import transaction


MAIL_DATA = open(
    os.path.join(os.path.dirname(__file__), 'mail.txt'), 'r').read()


class TestOGMailAddition(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestOGMailAddition, self).setUp()
        self.grant('Contributor', 'Editor', 'Member', 'Manager')

    def test_og_mail_behavior(self):
        mail = createContentInContainer(self.portal, 'ftw.mail.mail')
        self.assertTrue(
            IOGMailMarker.providedBy(mail),
            'ftw mail obj does not provide the OGMail behavior interface.')

    def test_title_accessor(self):
        mail = createContentInContainer(self.portal, 'ftw.mail.mail')
        self.assertEquals(u'[No Subject]', mail.title)
        self.assertEquals('[No Subject]', mail.Title())

        mail = createContentInContainer(
            self.portal, 'ftw.mail.mail',
            message=NamedBlobFile(MAIL_DATA, filename=u"mail.eml"))

        self.assertEquals(u'Die B\xfcrgschaft', mail.title)
        self.assertEquals('Die B\xc3\xbcrgschaft', mail.Title())

    def test_mail_behavior(self):
        mail = createContentInContainer(
            self.portal, 'ftw.mail.mail',
            message=NamedBlobFile(MAIL_DATA, filename=u"mail.eml"))
        transaction.commit()

        self.browser.open('%s/edit' % mail.absolute_url())
        self.browser.getControl(
            name='form.widgets.IOGMail.title').value = 'hanspeter'
        self.browser.getControl(name='form.buttons.save').click()

        self.assertEquals(u'hanspeter', mail.title)
        self.assertEquals('hanspeter', mail.Title())
