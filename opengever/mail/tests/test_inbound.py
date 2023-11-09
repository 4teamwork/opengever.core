from AccessControl import Unauthorized
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail import inbound
from ftw.mail.interfaces import IEmailAddress
from ftw.testbrowser import browsing
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.mail.interfaces import IInboundMailSettings
from opengever.mail.mail import MESSAGE_SOURCE_MAILIN
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing.assets import load
from plone import api
import email


class TestMailInboundSender(IntegrationTestCase):

    def setUp(self):
        super(TestMailInboundSender, self).setUp()
        self.login(self.regular_user)
        emailaddress = IEmailAddress(self.request)
        self.destination_addr = emailaddress.get_email_for_object(self.dossier)
        self.logout()

    @browsing
    def test_rejects_unknown_sender(self, browser):
        msg_txt = (
            'To: to@example.org\n'
            'From: unknown@example.org\n'
            'Subject: Test')

        browser.open(self.portal, {'mail': msg_txt}, 'mail-inbound')
        self.assertEqual(
            '77:Unknown sender. Permission denied.',
            browser.contents)

    @browsing
    def test_accepts_known_sender(self, browser):
        self.login(self.dossier_responsible)
        sender = self.regular_user.getProperty('email')
        msg_txt = (
            'To: %s\n'
            'From: %s\n'
            'Subject: Test' % (self.destination_addr, sender))

        with self.observe_children(self.dossier) as children:
            browser.open(self.portal, {'mail': msg_txt}, 'mail-inbound')

        self.assertEqual(
            '0:OK',
            browser.contents)

        created_mail = children['added'].pop()
        self.assertEqual(self.regular_user.getId(), created_mail.Creator())

    @browsing
    def test_sender_email_match_is_exact(self, browser):
        self.login(self.dossier_responsible)

        # User with similar email adress as regular_user
        plone_user = create(Builder('user')
               .named(u'additional', u'User')
               .with_email('oo@example.com')
               .with_userid('additional'))

        ogds_user = create(Builder('ogds_user')
                .id(plone_user.getId())
                .having(
                    email='oo@example.com',
                ))
        ogds_user.session.flush()

        msg_txt = (
            'To: %s\n'
            'From: %s\n'
            'Subject: Test' % (self.destination_addr, 'oo@example.com'))

        with self.observe_children(self.dossier) as children:
            browser.open(self.portal, {'mail': msg_txt}, 'mail-inbound')

        self.assertEqual(
            '77:Unable to create message. Permission denied.',
            browser.contents)

    @browsing
    def test_aliases_sender_email_to_user(self, browser):
        self.login(self.dossier_responsible)

        aliased_from = u'finanzen@example.org'
        aliased_to = self.regular_user.getId().decode('utf-8')

        api.portal.set_registry_record(
            'sender_aliases',
            {aliased_from: aliased_to},
            IInboundMailSettings)

        msg_txt = (
            'To: %s\n'
            'From: %s\n'
            'Subject: Test' % (self.destination_addr, aliased_from))

        with self.observe_children(self.dossier) as children:
            browser.open(self.portal, {'mail': msg_txt}, 'mail-inbound')

        self.assertEqual(
            '0:OK',
            browser.contents)

        created_mail = children['added'].pop()
        self.assertEqual(self.regular_user.getId(), created_mail.Creator())

    @browsing
    def test_sender_alias_email_is_case_insensitive(self, browser):
        self.login(self.dossier_responsible)

        aliased_from = u'finanzen@example.org'
        aliased_to = self.regular_user.getId().decode('utf-8')

        api.portal.set_registry_record(
            'sender_aliases',
            {aliased_from: aliased_to},
            IInboundMailSettings)

        msg_txt = (
            'To: %s\n'
            'From: %s\n'
            'Subject: Test' % (self.destination_addr, u'FinANZen@exAmple.org'))

        with self.observe_children(self.dossier) as children:
            browser.open(self.portal, {'mail': msg_txt}, 'mail-inbound')

        self.assertEqual(
            '0:OK',
            browser.contents)

        created_mail = children['added'].pop()
        self.assertEqual(self.regular_user.getId(), created_mail.Creator())

    @browsing
    def test_nonexistent_userid_for_aliased_sender_raises_unknown_sender(self, browser):
        self.login(self.dossier_responsible)

        aliased_from = u'finanzen@example.org'
        aliased_to = u'doesnt-exist'

        api.portal.set_registry_record(
            'sender_aliases',
            {aliased_from: aliased_to},
            IInboundMailSettings)

        msg_txt = (
            'To: %s\n'
            'From: %s\n'
            'Subject: Test' % (self.destination_addr, aliased_from))

        with self.observe_children(self.dossier) as children:
            browser.open(self.portal, {'mail': msg_txt}, 'mail-inbound')

        self.assertEqual(
            '77:Unknown sender. Permission denied.',
            browser.contents)


class TestMailInbound(FunctionalTestCase):

    MAIL_TEMPLATE = 'To: {}\nFrom: from@example.org\nSubject: Test'

    def test_raises_error_when_adding_mails_not_allowed(self):
        dossier = create(Builder("dossier"))
        dossier.manage_permission('ftw.mail: Add Inbound Mail',
                                  roles=[], acquire=False)
        to_addess = IEmailAddress(self.request).get_email_for_object(dossier)
        message = self.MAIL_TEMPLATE.format(to_addess)

        with self.assertRaises(Unauthorized):
            inbound.createMailInContainer(dossier, message)

    def test_raises_error_when_mail_not_in_addable_types(self):
        ttool = api.portal.get_tool('portal_types')
        dossier_fti = ttool.get('opengever.dossier.businesscasedossier')
        dossier_fti.allowed_content_types = tuple()

        dossier = create(Builder("dossier"))
        to_addess = IEmailAddress(self.request).get_email_for_object(dossier)
        message = self.MAIL_TEMPLATE.format(to_addess)

        with self.assertRaises(ValueError):
            inbound.createMailInContainer(dossier, message)

    def test_eml_mail_creation(self):
        dossier = create(Builder("dossier"))
        to_addess = IEmailAddress(self.request).get_email_for_object(dossier)

        message = self.MAIL_TEMPLATE.format(to_addess)
        obj = inbound.createMailInContainer(dossier, message)
        self.assertTrue(obj.preserved_as_paper)
        self.assertEqual(message, obj.message.data)
        self.assertEqual(MESSAGE_SOURCE_MAILIN, obj.message_source)
        self.assertEqual('Test.eml', obj.message.filename)
        self.assertEqual('message/rfc822', obj.message.contentType)

    def test_p7m_mail_creation(self):
        dossier = create(Builder("dossier"))
        to_address = IEmailAddress(self.request).get_email_for_object(dossier)

        msg = email.message_from_string(load('signed.p7m'))
        msg.replace_header('To', to_address)
        message = msg.as_string()

        obj = inbound.createMailInContainer(dossier, message)
        self.assertTrue(obj.preserved_as_paper)
        self.assertEqual(message, obj.message.data)
        self.assertEqual(MESSAGE_SOURCE_MAILIN, obj.message_source)
        self.assertEqual('Hello.p7m', obj.message.filename)
        self.assertEqual('application/pkcs7-mime', obj.message.contentType)

    def test_initialized_docproperties_default_values(self):
        dossier = create(Builder("dossier"))
        to_addess = IEmailAddress(self.request).get_email_for_object(dossier)

        PropertySheetSchemaStorage().clear()

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'textline', u'notrequired', u'Optional field with default', u'',
                required=False,
                default=u'Not required, still has default'
            )
            .with_field(
                'multiple_choice', u'languages', u'Languages', u'',
                required=True, values=[u'de', u'fr', u'en'],
                default={u'de', u'en'},
            )
        )

        message = self.MAIL_TEMPLATE.format(to_addess)

        obj = inbound.createMailInContainer(dossier, message)
        expected_defaults = {
            u'IDocument.default': {
                u'languages': set([u'de', u'en']),
                u'notrequired': u'Not required, still has default',
            },
        }
        self.assertEqual(
            expected_defaults,
            IDocumentCustomProperties(obj).custom_properties)
