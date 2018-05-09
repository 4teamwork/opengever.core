# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.assets import load
import base64


class TestCreateMail(IntegrationTestCase):

    def setUp(self):
        super(TestCreateMail, self).setUp()

    @browsing
    def test_create_mail_from_msg_converts_to_eml(self, browser):
        self.login(self.regular_user, browser)
        msg = base64.b64encode(load('testmail.msg'))
        browser.open(
            self.dossier.absolute_url(),
            data='{"@type": "ftw.mail.mail",'
                 '"message": {"data": "%s", "encoding": "base64", '
                 '"filename": "testmail.msg"}}' % msg,
            method='POST',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.assertEqual(browser.status_code, 201)
        mail = self.dossier.objectValues()[-1]
        self.assertEqual(mail.Title(), 'testmail')
        self.assertEqual(mail.message.filename, 'testmail.eml')
        self.assertIn('MIME-Version: 1.0', mail.message.data)
        self.assertEqual(mail.original_message.filename, 'testmail.msg')

    @browsing
    def test_create_mail_from_eml(self, browser):
        self.login(self.regular_user, browser)
        msg = base64.b64encode(load('mail_with_one_mail_attachment.eml'))
        browser.open(
            self.dossier.absolute_url(),
            data='{"@type": "ftw.mail.mail",'
                 '"message": {"data": "%s", "encoding": "base64", '
                 '"filename": "testmail.eml"}}' % msg,
            method='POST',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.assertEqual(browser.status_code, 201)
        mail = self.dossier.objectValues()[-1]
        self.assertEqual(mail.Title(), 'Äusseres Testmäil')
        self.assertEqual(mail.message.filename, 'ausseres-testmail.eml')
        self.assertEqual(mail.original_message, None)
