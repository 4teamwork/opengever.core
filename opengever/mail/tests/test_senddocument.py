from ftw.mail.utils import get_attachments
from ftw.testing.mailing import Mailing
from opengever.mail.behaviors import ISendableDocsContainer
from opengever.mail.interfaces import IDocumentSent
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create
from opengever.testing import create_client
from opengever.testing import create_ogds_user
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.component import provideHandler
from zope.intid.interfaces import IIntIds
import email
import quopri


TEST_FORM_DATA = {
    'as_links': False,
    'message': 'Foo bar',
    'subject': 'Test Subject',
    'extern_receiver': 'info@4teamwork.ch',
    'intern_receiver': ['hugo@boss.ch', ]}


class MockEvent(object):
    event_history = []

    def mock_handler(self, event):
        self.event_history.append(event, )

    def last_event(self):
        return self.event_history[-1]


class TestSendDocument(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestSendDocument, self).setUp()
        self.grant('Member', 'Contributor', 'Manager')

        create_client('plone')
        set_current_client_id(self.portal, clientid=u'plone')
        Mailing(self.portal).set_up()

    def test_dossier_is_sendable(self):
        dossier = create(Builder("dossier"))
        self.assertTrue(
            ISendableDocsContainer.providedBy(dossier))

    def test_document_size_validator(self):
        dossier = create(Builder("dossier"))
        document = create(Builder("document")
                          .within(dossier)
                          .attach_file_containing(600000 * '_FAKE_DATA'))

        mail = self.send_documents(dossier, [document, ])
        self.assertEquals(mail, None)
        self.assertPageContains(
            'The files you selected are larger than the maximum size')

        mail = self.send_documents(dossier, [document, ], as_links=True)
        self.assertCurrentUrl('%s#documents' % dossier.absolute_url())
        self.assert_mail_links_to(mail, document.absolute_url())

    def test_address_validator(self):
        dossier = create(Builder("dossier"))
        documents = [create(Builder("document").within(dossier)), ]

        mail = self.send_documents(
            dossier, documents, extern_receiver=None, intern_receiver=None)

        self.assertEquals(mail, None)
        self.assertPageContains('You have to select a intern \
                            or enter a extern mail-addres')

    def test_send_documents(self):
        create_ogds_user(
            TEST_USER_ID, firstname="Hugo", lastname="Boss", email="hugo@boss.ch")

        dossier = create(Builder("dossier"))
        documents = [create(Builder("document").within(dossier).with_dummy_content()), ]
        mail = self.send_documents(dossier, documents)

        self.assertEquals(TEST_FORM_DATA.get('subject'), mail.get('Subject'),
                          'The subject of the created mail is not correct')
        self.assertEquals(
            '"Boss Hugo \(test_user_1_\)" <hugo@boss.ch>',
            mail.get('From'),
            'The sender of the mail is incorrect.')
        self.assertIn(
            TEST_FORM_DATA.get('message'), mail.as_string(),
            'The message of the created mail is incorrect')

        self.assert_attachment(mail, 'test.doc', 'application/msword')

    def test_send_documents_with_non_ascii_message(self):
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

    def test_send_empty_documents(self):
        dossier = create(Builder("dossier"))
        document = create(Builder("document"))

        mail = self.send_documents(dossier, [document, ])

        self.assert_mail_links_to(mail, document.absolute_url())

    def test_send_documents_as_links(self):
        dossier = create(Builder("dossier"))
        document = create(Builder("document").with_dummy_content())

        mail = self.send_documents(dossier, [document, ], as_links=True)

        self.assert_mail_links_to(mail, document.absolute_url())

    def test_send_mails(self):
        dossier = create(Builder("dossier"))
        mails = [create(Builder("mail").within(dossier).with_dummy_message()), ]

        mail = self.send_documents(dossier, mails)
        self.assert_attachment(mail, 'testmail.eml', 'message/rfc822')

    def test_send_document_event(self):
        intids = getUtility(IIntIds)
        dossier = create(Builder("dossier"))
        documents = [create(Builder("document").within(dossier).with_dummy_content()), ]

        # mock event handler
        mock_event = MockEvent()
        provideHandler(factory=mock_event.mock_handler,
                       adapts=[IDocumentSent, ], )

        self.send_documents(dossier, documents)

        # check event
        event = mock_event.last_event()
        self.assertEquals(event.sender, TEST_USER_ID)
        self.assertEquals(event.receiver, TEST_FORM_DATA.get('extern_receiver'))
        self.assertEquals(event.object.getPhysicalPath(), dossier.getPhysicalPath())
        self.assertEquals(event.subject, TEST_FORM_DATA.get('subject'))
        self.assertEquals(event.message, TEST_FORM_DATA.get('message'))
        self.assertEquals(
            intids.getObject(event.intids[0]),
            documents[0])

    def send_documents(self, container, documents, **kwargs):
        documents = ['/'.join(doc.getPhysicalPath()) for doc in documents]
        data = '&'.join(['paths:list=%s' % path for path in documents])

        attr = TEST_FORM_DATA.copy()
        attr.update(kwargs)

        self.browser.open(
            '%s/send_documents' % container.absolute_url(),
            data=data)

        self.browser.getControl(name='form.widgets.documents_as_links:list').value = attr.get('as_links')
        self.browser.getControl(
            name='form.widgets.subject').value = attr.get('subject', '')
        self.browser.getControl(
            name='form.widgets.message').value = attr.get('message', '')
        if attr.get('extern_receiver', ''):
            self.browser.getControl(name='form.widgets.extern_receiver').value = attr.get('extern_receiver', '')

        self.browser.getControl(name='form.buttons.button_send').click()

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
