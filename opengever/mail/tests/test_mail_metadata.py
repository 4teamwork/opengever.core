from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail import utils
from opengever.document.behaviors import metadata
from opengever.document.interfaces import IDocumentSettings
from opengever.mail.mail import extract_email
from opengever.mail.mail import get_author_by_email
from opengever.testing import FunctionalTestCase
from opengever.testing.sql import create_ogds_user
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import getUtility
import os


MAIL_DATA = open(
    os.path.join(os.path.dirname(__file__), 'mail.txt'), 'r').read()


class TestMailMetadata(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestMailMetadata, self).setUp()
        self.grant('Contributor', 'Editor', 'Member', 'Manager')

    def get_header_date(self, mail):
        return datetime.fromtimestamp(utils.get_date_header(mail.msg, 'Date'))

    def get_preserved_as_papger_default(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(
            IDocumentSettings).preserved_as_paper_default

    def test_fill_metadata_of_new_mail(self):
        mail = create(Builder("mail").with_message(MAIL_DATA))
        mail_metadata = metadata.IDocumentMetadata(mail)

        self.assertIsNone(mail_metadata.description,
                          'Description has no value')

        self.assertEquals((), mail_metadata.keywords, 'Expect no keywords')

        self.assertIsNone(mail_metadata.foreign_reference,
                          'Foreign reference has no value')

        self.assertEquals(self.get_header_date(mail).date(),
                          mail_metadata.document_date)

        self.assertEquals(date.today(),
                          mail_metadata.receipt_date)

        self.assertIsNone(mail_metadata.delivery_date,
                          'Delivery date has no value')

        self.assertIsNone(mail_metadata.document_type,
                          'Document type has no value')

        self.assertIsNone(mail_metadata.digitally_available,
                          'Digitally available has no value')

        self.assertEquals(self.get_preserved_as_papger_default(),
                          mail_metadata.preserved_as_paper)

        self.assertIsNone(mail_metadata.archival_file,
                          'Archival file date has no value')

        self.assertIsNone(mail_metadata.thumbnail,
                          'Thumbnail has no value')

        self.assertIsNone(mail_metadata.preview,
                          'Preview has no value')

    def test_fill_mail_author_with_fullname_of_EXISTING_user(self):
        properties = {'firstname': 'Friedrich',
                      'lastname': u'H\xf6lderlin',
                      'email': 'from@example.org'}
        user = create_ogds_user('someuserid', **properties)

        mail = create(Builder("mail").with_message(MAIL_DATA))
        mail_metadata = metadata.IDocumentMetadata(mail)

        self.assertEquals(
            u'{0} {1}'.format(user.lastname, user.firstname),
            get_author_by_email(mail))

        self.assertEquals(
            get_author_by_email(mail),
            mail_metadata.document_author)

    def test_fill_mail_author_with_FROM_data_if_user_does_not_exist(self):

        mail = create(Builder("mail").with_message(MAIL_DATA))
        mail_metadata = metadata.IDocumentMetadata(mail)

        self.assertEquals(
            utils.get_header(mail.msg, 'From'),
            get_author_by_email(mail))

        self.assertEquals(
            get_author_by_email(mail),
            mail_metadata.document_author)

    def test_metadata_initialization_upgrade_step(self):
        fti = getUtility(IDexterityFTI, name=u'ftw.mail.mail')
        behaviors = list(fti.behaviors)
        behaviors.remove(
            u'opengever.document.behaviors.metadata.IDocumentMetadata')
        fti._updateProperty('behaviors', tuple(behaviors))

        mail = create(Builder("mail").with_message(MAIL_DATA))

        from opengever.mail.upgrades.to2200 import ActivateBehaviors
        ActivateBehaviors(self.portal.portal_setup)

        assert metadata.IDocumentMetadata.providedBy(mail)
        mail_metadata = metadata.IDocumentMetadata(mail)
        # The description is initialized wihtout the behavior, so the default
        # value is by another behavior with a description field.
        self.assertEquals(u'',
                          mail_metadata.description,
                          'Description has no value')

        self.assertEquals((), mail_metadata.keywords, 'Expect no keywords')

        self.assertIsNone(mail_metadata.foreign_reference,
                          'Foreign reference has no value')

        self.assertEquals(self.get_header_date(mail).date(),
                          mail_metadata.document_date)

        self.assertEquals(date.today(),
                          mail_metadata.receipt_date)

        self.assertIsNone(mail_metadata.delivery_date,
                          'Delivery date has no value')

        self.assertIsNone(mail_metadata.document_type,
                          'Document type has no value')

        self.assertIsNone(mail_metadata.digitally_available,
                          'Digitally available has no value')

        self.assertEquals(self.get_preserved_as_papger_default(),
                          mail_metadata.preserved_as_paper)

        self.assertIsNone(mail_metadata.archival_file,
                          'Archive file has no value')

        self.assertIsNone(mail_metadata.thumbnail,
                          'Thumbnail has no value')

        self.assertIsNone(mail_metadata.preview,
                          'Preview has no value')

    def test_mail_catalog_metadata(self):
        mail = create(Builder("mail").with_message(MAIL_DATA))

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
