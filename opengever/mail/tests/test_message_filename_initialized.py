from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail import inbound
from ftw.testbrowser import browsing
from opengever.mail.tests import MAIL_DATA
from opengever.testing import FunctionalTestCase


class TestMessageFilenameInitialized(FunctionalTestCase):

    def test_message_filename_initialized_with_builder(self):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        self.assertEquals('Die Buergschaft.eml', mail.get_filename())
        self.assertEquals('Die Buergschaft.eml', mail.message.filename)

    def test_filename_is_none_when_no_file_is_present(self):
        mail = create(Builder("mail"))
        self.assertIsNone(mail.get_filename())

    def test_message_filename_initialized_with_quickupload(self):
        dossier = create(Builder("dossier"))
        factory = IQuickUploadFileFactory(dossier)

        result = factory(filename='mail.eml',
                         title='',  # ignored by adapter
                         description='Description',  # ignored by adapter
                         content_type='message/rfc822',
                         data=MAIL_DATA,
                         portal_type='ftw.mail.mail')
        mail = result['success']
        self.assertEquals('Die Buergschaft.eml', mail.message.filename)

    def test_message_filename_initialzed_with_inboud_mail(self):
        dossier = create(Builder("dossier"))
        mail = inbound.createMailInContainer(dossier, MAIL_DATA)
        self.assertEquals('Die Buergschaft.eml', mail.message.filename)

    @browsing
    def test_message_filename_initialized_on_addview(self, browser):
        dossier = create(Builder("dossier"))
        browser.login().open(dossier, view='++add++ftw.mail.mail')
        browser.fill({
            'Raw Message': (MAIL_DATA, 'mail.eml', 'message/rfc822')
        }).submit()

        mail = browser.context
        self.assertEquals('Die Buergschaft.eml', mail.message.filename)
