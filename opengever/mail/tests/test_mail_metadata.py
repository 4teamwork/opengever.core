from collective.quickupload.interfaces import IQuickUploadFileFactory
from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.document.behaviors import metadata
from opengever.document.interfaces import IDocumentSettings
from opengever.mail.mail import extract_email
from opengever.mail.mail import get_author_by_email
from opengever.mail.tests.utils import get_header_date
from opengever.testing import FunctionalTestCase
from opengever.testing.sql import create_ogds_user
from pkg_resources import resource_string
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import getUtility


MAIL_DATA = resource_string('opengever.mail.tests', 'mail.txt')


def get_preserved_as_paper_default():
    registry = getUtility(IRegistry)
    return registry.forInterface(IDocumentSettings).preserved_as_paper_default


def set_preserved_as_paper_default(value):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IDocumentSettings)
    settings.preserved_as_paper_default = value


class TestMailMetadataWithBuilder(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestMailMetadataWithBuilder, self).setUp()
        self.grant('Contributor', 'Editor', 'Member', 'Manager')

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
        self.assertIsNone(mail.description,
                          'Description should have no value')

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
        factory = IQuickUploadFileFactory(dossier)

        result = factory(filename='mail.eml',
                         title='',  # ignored by adapter
                         description='Description',  # ignored by adapter
                         content_type='message/rfc822',
                         data=MAIL_DATA,
                         portal_type='ftw.mail.mail')
        mail = result['success']
        return mail


class TestMailUpgradeStep(FunctionalTestCase):

    def test_metadata_initialization_upgrade_step(self):
        fti = getUtility(IDexterityFTI, name=u'ftw.mail.mail')
        behaviors = list(fti.behaviors)
        behaviors.remove(
            u'opengever.document.behaviors.metadata.IDocumentMetadata')
        fti._updateProperty('behaviors', tuple(behaviors))

        # Set the registry default value for `preserved_as_paper` to
        # something else than the schema default
        set_preserved_as_paper_default(False)

        mail = create(Builder("mail").with_message(MAIL_DATA))

        from opengever.mail.upgrades.to3401 import ActivateBehaviors
        ActivateBehaviors(self.portal.portal_setup)

        assert metadata.IDocumentMetadata.providedBy(mail)
        mail = metadata.IDocumentMetadata(mail)
        # The description is initialized wihtout the behavior, so the default
        # value is by another behavior with a description field.
        self.assertEquals(u'',
                          mail.description,
                          'Description has no value')

        self.assertEquals((), mail.keywords, 'Expect no keywords')

        self.assertIsNone(mail.foreign_reference,
                          'Foreign reference has no value')

        self.assertEquals(get_header_date(mail).date(),
                          mail.document_date)

        self.assertEquals(None,
                          mail.receipt_date)

        self.assertIsNone(mail.delivery_date,
                          'Delivery date has no value')

        self.assertIsNone(mail.document_type,
                          'Document type has no value')

        self.assertTrue(mail.digitally_available,
                        'Digitally available should be True')

        self.assertEquals(get_preserved_as_paper_default(),
                          mail.preserved_as_paper)

        self.assertIsNone(mail.archival_file,
                          'Archive file has no value')

        self.assertIsNone(mail.thumbnail,
                          'Thumbnail has no value')

        self.assertIsNone(mail.preview,
                          'Preview has no value')


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
