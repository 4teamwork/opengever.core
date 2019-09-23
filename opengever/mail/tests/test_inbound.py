from AccessControl import Unauthorized
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail import inbound
from ftw.mail.interfaces import IEmailAddress
from opengever.mail.mail import MESSAGE_SOURCE_MAILIN
from opengever.testing import FunctionalTestCase
from opengever.testing.assets import load
from plone import api
import email


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
