from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.interfaces import IDocumentSettings
from opengever.mail.exceptions import AlreadyExtractedError
from opengever.mail.mail import IOGMailMarker
from opengever.mail.mail import NO_SUBJECT_TITLE_FALLBACK
from opengever.mail.tests import MAIL_DATA
from opengever.testing import FunctionalTestCase
from plone import api
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
import transaction


LINEBREAK_MESSAGETEXT = """Mime-Version: 1.0
Content-Type: multipart/mixed; boundary=908752978
To: to@example.org\nFrom: from@example.org
Subject: Attachment Test
Date: Thu, 01 Jan 1970 01:00:00 +0100\nMessage-Id: <1>


--908752978
Content-Disposition: attachment;
    filename=Projekt Test Inputvorschlag.doc
Content-Type: text/plain;
    name="Projekt Test Input
        vorschlag.doc"
Content-Transfer-Encoding: base64

w6TDtsOcCg==

--908752978--
"""


class TestOGMailAddition(FunctionalTestCase):
    """Test mail uploads."""

    def setUp(self):
        super(TestOGMailAddition, self).setUp()

        self.dossier = create(Builder('dossier'))

    def test_og_mail_behavior(self):
        mail = create(Builder("mail"))
        self.assertTrue(
            IOGMailMarker.providedBy(mail),
            'ftw mail obj does not provide the OGMail behavior interface.')

    def test_title_accessor(self):
        mail = create(Builder("mail"))
        self.assertEquals(NO_SUBJECT_TITLE_FALLBACK, mail.title)
        self.assertEquals(NO_SUBJECT_TITLE_FALLBACK, mail.Title())

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

    def test_copy_mail_preserves_metadata(self):
        dossier_1 = create(Builder('dossier'))
        dossier_2 = create(Builder('dossier'))
        mail = create(Builder('mail')
                      .within(dossier_1)
                      .with_message(MAIL_DATA))

        # can't set this with `having` as it is overwritten by an event handler
        mail.document_author = 'Hanspeter'
        mail.document_date = date(2014, 1, 5)
        mail.receipt_date = date(2014, 10, 1)

        # preserved on initial creation
        self.assertEqual('Hanspeter', mail.document_author)
        self.assertEqual(date(2014, 1, 5), mail.document_date)
        self.assertEqual(date(2014, 10, 1), mail.receipt_date)

        copy = api.content.copy(source=mail, target=dossier_2)
        # preserved on copy
        self.assertEqual('Hanspeter', copy.document_author)
        self.assertEqual(date(2014, 1, 5), copy.document_date)
        self.assertEqual(date(2014, 10, 1), copy.receipt_date)

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

    def test_update_filename_does_not_fail_for_mails_without_message(self):
        mail = create(Builder("mail").titled('Foo'))
        mail.title = u'Foo B\xe4r'
        mail.update_filename()

    def test_update_filename_sets_normalized_filename(self):
        mail = create(Builder('mail').with_dummy_message())
        mail.title = u'Foo B\xe4r'
        mail.update_filename()
        self.assertEqual(u'Foo Baer.eml', mail.message.filename)

    def test_get_attachments_returns_correct_descriptor_dict(self):
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_asset_message('mail_with_one_mail_attachment.eml'))

        expected_description = ({
            'content-type': 'message/rfc822',
            'filename': 'Inneres Testma\xcc\x88il ohne Attachments.eml',
            'position': 2,
            'size': 930,
        },)
        self.assertEqual(expected_description, mail.get_attachments())

    def test_get_attachments_returns_empty_list_for_mails_without_attachments(self):  # noqa
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_message(MAIL_DATA))
        self.assertEqual(tuple(), mail.get_attachments())

    def test_truthy_has_attachmentes(self):
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_asset_message('mail_with_one_mail_attachment.eml'))

        self.assertTrue(mail.has_attachments())

    def test_falsy_has_attachments(self):
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_message(MAIL_DATA))
        self.assertFalse(mail.has_attachments())

    def test_extracting_into_unsupported_container_raises_error(self):
        mail = create(Builder('mail')
                      .with_asset_message('mail_with_one_mail_attachment.eml'))

        with self.assertRaises(RuntimeError):
            mail.extract_attachment_into_parent(position=2)


class TestExtractMail(FunctionalTestCase):

    def setUp(self):
        super(TestExtractMail, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.mail = create(Builder('mail')
                           .within(self.dossier)
                           .with_asset_message(
                               'mail_with_multiple_attachments.eml'))

    def test_attachment_can_only_be_extracted_once(self):
        self.mail.extract_attachment_into_parent(4)
        with self.assertRaises(AlreadyExtractedError):
            self.mail.extract_attachment_into_parent(4)

    def test_extracting_attachment_updates_attachment_info(self):
        info = self.mail._get_attachment_info(4)
        expected_info = {
            'content-type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'filename': 'word_document.docx',
            'position': 4,
            'size': 22962}
        self.assertEqual(info, expected_info)

        doc = self.mail.extract_attachment_into_parent(4)
        info = self.mail._get_attachment_info(4)
        expected_info.update({
            'extracted': True,
            'extracted_document_uid': IUUID(doc)})
        self.assertEqual(info, expected_info)


class TestExtractMailInDossier(FunctionalTestCase):
    """Test the conversion of emails into OG data types."""

    def setUp(self):
        super(TestExtractMailInDossier, self).setUp()
        self.parent = self.setup_parent()

    def setup_parent(self):
        return create(Builder('dossier'))

    def test_extract_attachment_sets_default_values_correctly_on_document(self):  # noqa
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IDocumentSettings)
        proxy.preserved_as_paper_default = False
        transaction.commit()

        mail = create(Builder('mail')
                      .within(self.parent)
                      .with_asset_message('mail_with_one_docx_attachment.eml'))
        doc = mail.extract_attachment_into_parent(position=2)
        self.assertEqual(doc.portal_type, 'opengever.document.document')
        self.assertEqual('word_document', doc.Title())
        self.assertFalse(doc.preserved_as_paper)
        self.assertTrue(doc.digitally_available)

    def test_extract_mail_from_mail_with_one_attachment(self):
        mail = create(Builder('mail')
                      .within(self.parent)
                      .with_asset_message('mail_with_one_mail_attachment.eml'))

        extracted = mail.extract_attachment_into_parent(position=2)
        self.assertEqual(extracted.portal_type, 'ftw.mail.mail')
        self.assertEquals(u'Inneres Testm\xe4il ohne Attachments',
                          extracted.Title().decode('utf-8'))

    def test_extract_p7m_from_mail_creates_mail(self):
        mail = create(Builder('mail')
                      .within(self.parent)
                      .with_asset_message('mail_with_one_p7m_attachment.eml'))

        extracted = mail.extract_attachment_into_parent(position=2)
        self.assertEqual(extracted.portal_type, 'ftw.mail.mail')

    def test_extract_nested_mail_from_mail_with_attachments(self):
        mail = create(Builder('mail')
                      .within(self.parent)
                      .with_asset_message('mail_with_nested_attachments.eml'))

        positions = [attachment['position'] for attachment in
                     mail.get_attachments()]

        extracted = mail.extract_attachments_into_parent(positions).values()
        self.assertEqual(6, len(extracted))

        outer_mail = extracted[0]
        inner_mail = extracted[1]

        self.assertEqual(u'Mehrere Anh\xe4nge',
                         outer_mail.Title().decode('utf-8'))
        self.assertEqual(u'Inneres Testm\xe4il ohne Attachments',
                         inner_mail.Title().decode('utf-8'))

    def test_extract_multiple_attachments(self):
        mail = create(Builder('mail')
                      .within(self.parent)
                      .with_asset_message(
                          'mail_with_multiple_attachments.eml'))

        positions = [attachment['position'] for attachment in
                     mail.get_attachments()]

        extracted = mail.extract_attachments_into_parent(positions).values()
        self.assertEqual(3, len(extracted))
        extracted_mail = extracted[0]
        doc = extracted[1]
        text = extracted[2]

        self.assertEqual(u'Inneres Testm\xe4il ohne Attachments',
                         extracted_mail.Title().decode('utf-8'))
        self.assertEqual('word_document', doc.Title())
        self.assertEqual('Text', text.Title())

    def test_extracting_line_break_mail(self):
        mail = create(Builder('mail')
                      .within(self.parent)
                      .with_message(LINEBREAK_MESSAGETEXT))

        doc = mail.extract_attachment_into_parent(position=1)
        self.assertEquals('Projekt Test Inputvorschlag', doc.Title())


class TestExtractMailInInbox(TestExtractMailInDossier):
    """Test email to OG conversion from the inbox."""

    def setup_parent(self):
        return create(Builder('inbox'))


class TestExtractMailInTask(TestExtractMailInDossier):
    """Test email to OG conversion from a task."""

    def setup_parent(self):
        self.dossier = create(Builder('dossier'))
        return create(Builder('task').within(self.dossier))
