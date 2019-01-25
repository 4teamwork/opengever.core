from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail import inbound
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from opengever.document.interfaces import IDocumentSettings
from opengever.mail.mail import extract_email
from opengever.mail.mail import get_author_by_email
from opengever.mail.mail import MESSAGE_SOURCE_DRAG_DROP_UPLOAD
from opengever.mail.tests import MAIL_DATA
from opengever.mail.tests.utils import get_header_date
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing.sql import create_ogds_user
from plone.registry.interfaces import IRegistry
from unittest import TestCase
from zope.component import getUtility


def get_preserved_as_paper_default():
    registry = getUtility(IRegistry)
    return registry.forInterface(IDocumentSettings).preserved_as_paper_default


def set_preserved_as_paper_default(value):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IDocumentSettings)
    settings.preserved_as_paper_default = value


class TestMailMetadataWithBuilder(FunctionalTestCase):

    def create_mail(self):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        return mail

    def create_user(self):
        user_properties = {'firstname': 'Friedrich',
                           'lastname': u'H\xf6lderlin',
                           'email': 'from@example.org'}
        user = create_ogds_user('someuserid', **user_properties)
        return user

    def test_fill_metadata_of_new_mail(self):
        mail = self.create_mail()
        self.assertEquals(u'', mail.description)

        self.assertEquals((), mail.keywords, 'Expected no keywords')

        self.assertIsNone(mail.foreign_reference,
                          'Foreign reference should have no value')

        self.assertEquals(get_header_date(mail).date(),
                          mail.document_date)

        self.assertEquals(date.today(),
                          mail.receipt_date)

        self.assertIsNone(mail.delivery_date,
                          'Delivery date should have no value')

        self.assertIsNone(mail.document_type,
                          'Document type should have no value')

        self.assertTrue(mail.digitally_available,
                        'Digitally available should be True')

        self.assertEquals(get_preserved_as_paper_default(),
                          mail.preserved_as_paper)

        self.assertIsNone(mail.archival_file,
                          'Archival file should have no value')

        self.assertIsNone(mail.thumbnail,
                          'Thumbnail should have no value')

        self.assertIsNone(mail.preview,
                          'Preview should have no value')

    def test_fill_mail_author_with_fullname_of_EXISTING_user(self):
        user = self.create_user()
        mail = self.create_mail()
        self.assertEquals(
            u'{0} {1}'.format(user.lastname, user.firstname),
            get_author_by_email(mail))

        self.assertEquals(
            get_author_by_email(mail),
            mail.document_author)

    def test_fill_mail_author_with_FROM_data_if_user_does_not_exist(self):
        mail = self.create_mail()

        self.assertEquals(
            u'Freddy H\xf6lderlin <from@example.org>',
            get_author_by_email(mail))

        self.assertEquals(
            get_author_by_email(mail),
            mail.document_author)

    def test_mail_catalog_metadata(self):
        mail = self.create_mail()
        brain = self.portal.portal_catalog(portal_type='ftw.mail.mail')[0]

        self.assertEquals(mail.document_date,
                          brain.document_date)

        self.assertEquals(mail.document_author,
                          brain.document_author)

        self.assertEquals(mail.receipt_date,
                          brain.receipt_date)

        self.assertEquals('',
                          brain.checked_out,
                          'Checked out, should be empty')


class TestMailMetadataWithQuickupload(TestMailMetadataWithBuilder):

    def create_mail(self):
        dossier = create(Builder("dossier"))
        mail = create(Builder('quickuploaded_mail')
                      .within(dossier)
                      .with_message(MAIL_DATA))
        return mail

    def test_mail_message_source(self):
        mail = self.create_mail()

        self.assertEqual(MESSAGE_SOURCE_DRAG_DROP_UPLOAD, mail.message_source)


class TestMailMetadataWithAddView(TestMailMetadataWithBuilder):

    def create_mail(self):
        """Add mails over a plone view since builders implement their own
        instance construction.
        """

        with browser(self.app):
            dossier = create(Builder("dossier"))
            browser.login().open(dossier, view='++add++ftw.mail.mail')
            browser.fill({
                'Raw Message': (MAIL_DATA, 'mail.eml', 'message/rfc822')
            }).submit()

            mail = browser.context
            return mail


class TestMailAuthorResolving(IntegrationTestCase):

    @browsing
    def test_editing_mail_with_a_userid_as_author_resolves_to_fullname(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, view='edit')
        browser.fill({'Author': u'kathi.barfuss'})
        browser.click_on('Save')

        self.assertEquals(u'B\xe4rfuss K\xe4thi', self.mail_eml.document_author)
        self.assertEquals(u'B\xe4rfuss K\xe4thi', obj2brain(self.mail_eml).document_author)

    @browsing
    def test_editing_mail_with_a_real_name_as_author_dont_change_author_name(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, view='edit')
        browser.fill({'Author': u'Muster Peter'})
        browser.click_on('Save')

        self.assertEquals('Muster Peter', self.mail_eml.document_author)


class TestMailPreservedAsPaperDefault(FunctionalTestCase):

    def create_mail_quickupload(self):
        dossier = create(Builder("dossier"))
        mail = create(Builder('quickuploaded_mail')
                      .within(dossier)
                      .with_message(MAIL_DATA))
        return mail

    def create_mail_inbound(self):
        dossier = create(Builder("dossier"))
        mail = inbound.createMailInContainer(dossier, MAIL_DATA)
        return mail

    def test_value_if_default_is_true(self):
        set_preserved_as_paper_default(True)

        quickuploaded_mail = self.create_mail_quickupload()
        self.assertEquals(True, quickuploaded_mail.preserved_as_paper)

        inbound_mail = self.create_mail_inbound()
        self.assertEquals(True, inbound_mail.preserved_as_paper)

    def test_value_if_default_is_false(self):
        set_preserved_as_paper_default(False)

        quickuploaded_mail = self.create_mail_quickupload()
        self.assertEquals(False, quickuploaded_mail.preserved_as_paper)

        inbound_mail = self.create_mail_inbound()
        self.assertEquals(False, inbound_mail.preserved_as_paper)


class TestEmailRegex(TestCase):

    def test_email_format_1(self):
        header_from = 'Hans Muster <hans@example.org>'
        self.assertEquals('hans@example.org', extract_email(header_from))

    def test_email_format_2(self):
        header_from = '"Hans Muster" <hans@example.org>'
        self.assertEquals('hans@example.org', extract_email(header_from))

    def test_email_format_3(self):
        header_from = 'Muster, Hans <hans@example.org>'
        self.assertEquals('hans@example.org', extract_email(header_from))

    def test_email_format_4(self):
        header_from = '<hans@example.org>'
        self.assertEquals('hans@example.org', extract_email(header_from))

    def test_email_format_5(self):
        header_from = 'hans@example.org'
        self.assertEquals('hans@example.org', extract_email(header_from))

    def test_email_format_6(self):
        header_from = 'hAnS@Example.Org'
        self.assertEquals('hans@example.org', extract_email(header_from))

    def test_no_match(self):
        header_from = 'example.org'
        self.assertEquals('example.org', extract_email(header_from))
