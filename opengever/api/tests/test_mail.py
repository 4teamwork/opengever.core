# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.assets import load
import base64
import json


class TestCreateMail(IntegrationTestCase):

    def setUp(self):
        super(TestCreateMail, self).setUp()

    @browsing
    def test_create_mail_from_msg_converts_to_eml(self, browser):
        self.login(self.regular_user, browser)
        msg = base64.b64encode(load('testmail.msg'))

        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier.absolute_url(),
                data='{"@type": "ftw.mail.mail",'
                     '"message": {"data": "%s", "encoding": "base64", '
                     '"filename": "testmail.msg"}}' % msg,
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})

        self.assertEqual(browser.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), 'testmail')
        self.assertEqual(mail.message.filename, 'testmail.eml')
        self.assertIn('MIME-Version: 1.0', mail.message.data)
        self.assertEqual(mail.original_message.filename, 'testmail.msg')

    @browsing
    def test_create_mail_from_eml(self, browser):
        self.login(self.regular_user, browser)
        msg = base64.b64encode(load('mail_with_one_mail_attachment.eml'))

        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier.absolute_url(),
                data='{"@type": "ftw.mail.mail",'
                     '"message": {"data": "%s", "encoding": "base64", '
                     '"filename": "testmail.eml"}}' % msg,
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})


        self.assertEqual(browser.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), 'Äusseres Testmäil')
        self.assertEqual(mail.message.filename, 'ausseres-testmail.eml')
        self.assertEqual(mail.original_message, None)

    @browsing
    def test_uses_title_if_given(self, browser):
        self.login(self.regular_user, browser)
        msg = base64.b64encode(load('mail_with_one_mail_attachment.eml'))

        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier.absolute_url(),
                data=json.dumps({"@type": "ftw.mail.mail",
                                 "message": {"data": msg,
                                             "encoding": "base64",
                                             "filename": "testmail.eml"},
                                 "title": "Separate title"}),
                method='POST',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})

        self.assertEqual(browser.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), 'Separate title')
        self.assertEqual(mail.message.filename, 'separate-title.eml')
        self.assertEqual(mail.original_message, None)


class TestPatchMail(IntegrationTestCase):

    @browsing
    def test_updating_the_title(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.mail.absolute_url(),
            data=json.dumps({'title': u'New title'}),
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})

        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.mail.Title(), 'New title')
        self.assertEqual(self.mail.title, u'New title')

    @browsing
    def test_updating_other_metadata(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.mail.absolute_url(),
            data=json.dumps({'description': u'Lorem ipsum'}),
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})

        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.mail.title, u'Die B\xfcrgschaft')
        self.assertEqual(self.mail.description, 'Lorem ipsum')
