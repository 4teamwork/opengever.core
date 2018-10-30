from ftw.testbrowser import restapi
from opengever.mail.mail import IOGMail
from opengever.testing import IntegrationTestCase
from opengever.testing.assets import load
from plone.namedfile.file import NamedBlobFile
import base64


class TestGetMail(IntegrationTestCase):

    @restapi
    def test_contains_also_original_message(self, api_client):
        self.login(self.regular_user, api_client)
        IOGMail(self.mail_eml).original_message = NamedBlobFile(data='__DATA__', filename=u'testmail.msg')

        api_client.open(self.mail_eml)
        self.assertEqual(200, api_client.status_code)
        expected_message = {
            u'content-type': u'application/vnd.ms-outlook',
            u'download': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-24'
                         u'/@@download/original_message',
            u'filename': u'testmail.msg',
            u'size': 8,
        }
        self.assertEqual(expected_message, api_client.contents.get('original_message'))


class TestCreateMail(IntegrationTestCase):

    @restapi
    def test_create_mail_from_msg_converts_to_eml(self, api_client):
        self.login(self.regular_user, api_client)
        msg = base64.b64encode(load('testmail.msg'))
        data = {"@type": "ftw.mail.mail", "message": {"data": msg, "encoding": "base64", "filename": "testmail.msg"}}

        with self.observe_children(self.dossier) as children:
            api_client.open(self.dossier, data=data)

        self.assertEqual(api_client.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), 'testmail')
        self.assertEqual(mail.message.filename, 'testmail.eml')
        self.assertIn('MIME-Version: 1.0', mail.message.data)
        self.assertEqual(mail.original_message.filename, 'testmail.msg')

    @restapi
    def test_create_mail_from_eml(self, api_client):
        self.login(self.regular_user, api_client)
        msg = base64.b64encode(load('mail_with_one_mail_attachment.eml'))
        data = {"@type": "ftw.mail.mail", "message": {"data": msg, "encoding": "base64", "filename": "testmail.eml"}}
        with self.observe_children(self.dossier) as children:
            api_client.open(self.dossier, data=data)

        self.assertEqual(api_client.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), '\xc3\x84usseres Testm\xc3\xa4il')
        self.assertEqual(mail.message.filename, 'Aeusseres Testmaeil.eml')
        self.assertEqual(mail.original_message, None)

    @restapi
    def test_uses_title_if_given(self, api_client):
        self.login(self.regular_user, api_client)
        msg = base64.b64encode(load('mail_with_one_mail_attachment.eml'))
        data = {
            "@type": "ftw.mail.mail",
            "message": {"data": msg, "encoding": "base64", "filename": "testmail.eml"},
            "title": "Separate title",
        }
        with self.observe_children(self.dossier) as children:
            api_client.open(self.dossier, data=data)

        self.assertEqual(api_client.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), 'Separate title')
        self.assertEqual(mail.message.filename, 'Separate title.eml')
        self.assertEqual(mail.original_message, None)


class TestPatchMail(IntegrationTestCase):

    @restapi
    def test_updating_the_title(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.mail_eml, data={'title': u'New title'}, method='PATCH')

        self.assertEqual(api_client.status_code, 204)
        self.assertEqual(self.mail_eml.Title(), 'New title')
        self.assertEqual(self.mail_eml.title, u'New title')

    @restapi
    def test_updating_other_metadata(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.mail_eml, data={'description': u'Lorem ipsum'}, method='PATCH')

        self.assertEqual(api_client.status_code, 204)
        self.assertEqual(self.mail_eml.title, u'Die B\xfcrgschaft')
        self.assertEqual(self.mail_eml.description, 'Lorem ipsum')
