from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.utils import get_attachments
from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.activity.mailer import process_mail_queue
from opengever.mail.behaviors import ISendableDocsContainer
from opengever.mail.interfaces import IDocumentSent
from opengever.testing import FunctionalTestCase
from opengever.testing.event_recorder import get_last_recorded_event
from opengever.testing.event_recorder import register_event_recorder
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import email
import quopri
import transaction


TEST_FORM_DATA = {
    'as_links': False,
    'message': 'Foo bar',
    'subject': 'Test Subject',
    'extern_receiver': 'info@example.com',
    'intern_receiver': ['hugo@example.org', ]}


class TestSendDocument(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestSendDocument, self).setUp()

        create(Builder('fixture')
               .with_user(firstname="Test", lastname="User")
               .with_org_unit()
               .with_admin_unit(public_url='http://nohost/plone'))

        Mailing(self.portal).set_up()

    def tearDown(self):
        process_mail_queue()
        Mailing(self.portal).tear_down()

    def test_dossier_is_sendable(self):
        dossier = create(Builder("dossier"))
        self.assertTrue(
            ISendableDocsContainer.providedBy(dossier))

    @browsing
    def test_document_size_validator(self, browser):
        dossier = create(Builder("dossier"))
        document = create(Builder("document")
                          .within(dossier)
                          .attach_file_containing(600000 * '_FAKE_DATA'))

        mail = self.send_documents(dossier, [document, ])
        self.assertEquals(mail, None)
        self.assertEquals(
            ['The files you selected are larger than the maximum size'],
            browser.css('#formfield-form-widgets-documents .error').text)

        mail = self.send_documents(dossier, [document, ], as_links=True)
        self.assertEquals('%s#documents' % dossier.absolute_url(), browser.url)
        self.assert_mail_links_to(mail, document.absolute_url())

    @browsing
    def test_address_validator(self, browser):
        dossier = create(Builder("dossier"))
        documents = [create(Builder("document").within(dossier)), ]

        mail = self.send_documents(
            dossier, documents, extern_receiver=None, intern_receiver=None)

        self.assertEquals(mail, None)
        self.assertEquals(
            ['You have to select a intern or enter a extern mail-addres'],
            browser.css('div.error').text)

    @browsing
    def test_send_documents(self, browser):
        dossier = create(Builder("dossier"))
        documents = [create(Builder("document")
                            .within(dossier)
                            .without_default_title()
                            .with_dummy_content()), ]
        mail = self.send_documents(dossier, documents)

        self.assertEquals(TEST_FORM_DATA.get('subject'), mail.get('Subject'),
                          'The subject of the created mail is not correct')
        self.assertEquals(
            '"User Test \(test_user_1_\)" <test@example.org>',
            mail.get('From'),
            'The sender of the mail is incorrect.')
        self.assertIn(
            TEST_FORM_DATA.get('message'), mail.as_string(),
            'The message of the created mail is incorrect')

        self.assert_attachment(mail, 'test.doc', 'application/msword')

    @browsing
    def test_send_documents_with_non_ascii_message(self, browser):
        dossier = create(Builder("dossier"))
        documents = [create(Builder("document").within(dossier).with_dummy_content()), ]

        non_ascii_message = """
Als Beilage erhalten Sie:\r\n\r\n\xe2\x80\xa2\tPensionierten
Schreiben f\xc3\xbcr Hugo Boss\r\n\xe2\x80\xa2\tPensionierten-Schreiben
f\xc3\xbcr Ernst Franz\r\n\r\nBesten Dank im Voraus"""

        mail = self.send_documents(dossier, documents, message=non_ascii_message)
        self.assertIn(
            quopri.encodestring(non_ascii_message), mail.as_string(),
            'The message(non ascii) of the created mail is incorrect')

    @browsing
    def test_send_empty_documents(self, browser):
        dossier = create(Builder("dossier"))
        document = create(Builder("document").within(dossier))

        mail = self.send_documents(dossier, [document, ])

        self.assert_mail_links_to(mail, document.absolute_url())

    @browsing
    def test_send_documents_as_links(self, browser):
        dossier = create(Builder("dossier"))
        document = create(Builder("document")
                          .within(dossier)
                          .with_dummy_content())

        mail = self.send_documents(dossier, [document, ], as_links=True)

        self.assert_mail_links_to(mail, document.absolute_url())

    @browsing
    def test_send_mails(self, browser):
        dossier = create(Builder("dossier"))
        mails = [create(Builder("mail").within(dossier).with_dummy_message()), ]

        mail = self.send_documents(dossier, mails)
        self.assert_attachment(mail, 'No Subject.eml', 'message/rfc822')

        attachment = mail.get_payload()[1].get_payload()[0]
        self.assertIn(
            'foobar', attachment.get_payload(),
            'Attached mails should not be base64 encoded')

    @browsing
    def test_send_document_event(self, browser):
        intids = getUtility(IIntIds)
        dossier = create(Builder("dossier"))
        documents = [create(Builder("document").within(dossier).with_dummy_content()), ]

        register_event_recorder(IDocumentSent)
        transaction.commit()

        self.send_documents(dossier, documents)

        event = get_last_recorded_event()
        self.assertEquals(event.sender, TEST_USER_ID)
        self.assertEquals(event.receiver, TEST_FORM_DATA.get('extern_receiver'))
        self.assertEquals(event.subject, TEST_FORM_DATA.get('subject'))
        self.assertEquals(event.message, TEST_FORM_DATA.get('message'))
        self.assertEquals(event.intids, map(intids.getId, documents))

    @browsing
    def test_send_msg_if_there_is_a_original_message(self, browser):
        dossier = create(Builder("dossier"))
        mail = create(Builder("mail").within(dossier)
                      .with_dummy_message()
                      .with_dummy_original_message())

        mail = self.send_documents(dossier, [mail])

        self.assert_attachment(mail, 'No Subject.msg', 'application/vnd.ms-outlook')


    @browsing
    def test_sent_mail_gets_filed_in_dossier(self, browser):
        dossier = create(Builder("dossier"))
        document = create(Builder("document")
                          .within(dossier)
                          .with_dummy_content())

        self.send_documents(dossier, [document], file_copy_in_dossier=True)

        self.assertIn('document-2', dossier,
                      "Sent mail should be archived in dossier")

        filed_mail = dossier.restrictedTraverse('document-2')
        self.assertEquals(date.today(), filed_mail.delivery_date,
                          "Filed mail should have a delivery date of today")

        self.assertEquals(u'Test Subject', filed_mail.title,
                          "Filed mail should have subject as title")

        self.assertEquals(u'User Test', filed_mail.document_author,
                          "Author of filed mail should be name of OGDS user")

    @browsing
    def test_do_not_create_mail_archive_if_dossier_is_resolved(self, browser):
        dossier = create(Builder("dossier").in_state('dossier-state-resolved'))
        document = create(Builder("document").with_dummy_content())

        self.send_documents(dossier, [document], file_copy_in_dossier=True)

        self.assertEqual(
            [], dossier.listFolderContents(),
            "Sent mail shouldn't be archived in the dossier because "
            "the dossier is not in an open state.")

    @browsing
    def test_file_copy_field_is_shown_for_open_dossier(self, browser):
        fieldname = 'file_copy_in_dossier'
        dossier = create(Builder("dossier").in_state('dossier-state-active'))

        browser.login().open(dossier, view="send_documents")

        field = browser.find('File a copy of the sent mail in dossier')

        self.assertTrue(
            field,
            "The field should be available and be visible. "
            "The browser wasn't able to find the field. "
            "Available fields are: {}".format(
                browser.css('input[name^="form.widgets"]'))
            )

        self.assertEqual(
            'checkbox', field.type,
            "The field {} is not visible. See the field: {}".format(
                fieldname, field))

    @browsing
    def test_file_copy_field_not_shown_for_closed_dossier(self, browser):
        dossier = create(Builder("dossier").in_state('dossier-state-resolved'))

        browser.login().open(dossier, view="send_documents")

        field = browser.find('File a copy of the sent mail in dossier')
        self.assertEquals('disabled', field.get('disabled'))
        self.assertIsNone(field.get('checked'))

    @browsing
    def test_file_copy_field_not_shown_if_not_on_dossier(self, browser):
        inbox = create(Builder('inbox'))

        browser.login().open(inbox, view="send_documents")

        field = browser.find('File a copy of the sent mail in dossier')
        self.assertEquals('disabled', field.get('disabled'))
        self.assertIsNone(field.get('checked'))

    def send_documents(self, container, documents, browser=default_browser, **kwargs):
        documents = ['/'.join(doc.getPhysicalPath()) for doc in documents]
        attr = TEST_FORM_DATA.copy()
        attr.update(kwargs)

        browser.login().open(container,
                             {'paths:list': documents},
                             view='send_documents')
        browser.fill({'Send documents only als links': attr.get('as_links'),
                      'Subject': attr.get('subject', ''),
                      'Message': attr.get('message', '')})

        if attr.get('extern_receiver', ''):
            browser.fill({'Extern receiver': attr.get('extern_receiver')})

        if attr.get('intern_receiver', None):
            form = browser.find_form_by_field('Intern receiver')
            form.find_widget('Intern receiver').fill(
                attr.get('intern_receiver'))

        browser.click_on('Send')

        return self.get_mail()

    def get_mail(self):
        if Mailing(self.portal).has_messages():
            data = Mailing(self.portal).pop()
            return email.message_from_string(data)

    def assert_attachment(self, mail, filename, content_type):
        attachments = get_attachments(mail)
        self.assertEquals(1, len(attachments))
        self.assertEquals(filename, attachments[0].get('filename'))
        self.assertEquals(content_type, attachments[0].get('content-type'))

    def assert_mail_links_to(self, mail, url):
        self.assertIn(url, mail.as_string(),
                      'The link to the document of the created mail is missing.')
