from ftw.testbrowser import browsing
from opengever.mail.mail import IOGMail
from opengever.testing import IntegrationTestCase
from opengever.testing.assets import load
from plone.namedfile.file import NamedBlobFile
import base64
import json


class TestGetMail(IntegrationTestCase):

    @browsing
    def test_contains_also_original_message(self, browser):
        self.login(self.regular_user, browser)
        IOGMail(self.mail_eml).original_message = NamedBlobFile(
            data='__DATA__', filename=u'testmail.msg')

        browser.open(self.mail_eml.absolute_url(), method='GET',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})
        self.assertEqual(200, browser.status_code)
        expected_message = {
            u'content-type': u'application/vnd.ms-outlook',
            u'download': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-30'
                         u'/@@download/original_message',
            u'filename': u'testmail.msg',
            u'size': 8,
        }
        self.assertEqual(expected_message, browser.json.get('original_message'))


class TestCreateMail(IntegrationTestCase):

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
        self.assertEqual(mail.Title(), '\xc3\x84usseres Testm\xc3\xa4il')
        self.assertEqual(mail.message.filename, 'Aeusseres Testmaeil.eml')
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
        self.assertEqual(mail.message.filename, 'Separate title.eml')
        self.assertEqual(mail.original_message, None)


class TestPatchMail(IntegrationTestCase):

    @browsing
    def test_updating_the_title(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.mail_eml.absolute_url(),
            data=json.dumps({'title': u'New title'}),
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})

        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.mail_eml.Title(), 'New title')
        self.assertEqual(self.mail_eml.title, u'New title')

    @browsing
    def test_updating_other_metadata(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.mail_eml.absolute_url(),
            data=json.dumps({'description': u'Lorem ipsum'}),
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})

        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.mail_eml.title, u'Die B\xfcrgschaft')
        self.assertEqual(self.mail_eml.description, 'Lorem ipsum')
