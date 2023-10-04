from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCSolrIntegrationTestCase
import jwt


class TestOfficeconnectorMailAPIWithAttach(OCSolrIntegrationTestCase):

    features = ("!officeconnector-checkout", "officeconnector-attach")

    @browsing
    def test_attach_to_email_eml(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.mail_eml)

        self.assertIsNotNone(oc_url)
        self.assertEqual(200, browser.status_code)

        expected_token = {
            u"action": u"attach",
            u"documents": [u"createemails00000000000000000001"],
            u"exp": 4121033100,
            u"sub": u"kathi.barfuss",
            u"url": u"http://nohost/plone/oc_attach",
        }
        raw_token = oc_url.split(":")[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u"bcc": u"1014013300@example.org",
            u"content-type": u"message/rfc822",
            u"csrf-token": u"86ecf9b4135514f8c94c61ce336a4b98b4aaed8a",
            u"document-url": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/"
                             u"document-29",
            u"download": u"download",
            u"filename": u"Die Buergschaft.eml",
            u"title": u"Die B\xfcrgschaft",
            u"uuid": u"createemails00000000000000000001",
            u'version': 0,
        }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(expected_payloads, payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEqual(file_contents, self.mail_eml.get_file().data)

    @browsing
    def test_attach_to_email_msg(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.mail_msg)

        self.assertIsNotNone(oc_url)
        self.assertEqual(200, browser.status_code)

        expected_token = {
            u"action": u"attach",
            u"documents": [u"createemails00000000000000000002"],
            u"exp": 4121033100,
            u"sub": u"kathi.barfuss",
            u"url": u"http://nohost/plone/oc_attach",
        }
        raw_token = oc_url.split(":")[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u"bcc": u"1014013300@example.org",
            u"content-type": u"application/vnd.ms-outlook",
            u"csrf-token": u"86ecf9b4135514f8c94c61ce336a4b98b4aaed8a",
            u"document-url": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/"
                             u"document-30",
            u"download": u"@@download/original_message",
            u"filename": u"No Subject.msg",
            u"title": u"[No Subject]",
            u"uuid": u"createemails00000000000000000002",
            u'version': 0,
        }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(expected_payloads, payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEqual(file_contents, self.mail_msg.get_file().data)

    @browsing
    def test_attach_many_to_email_open(self, browser):
        self.login(self.regular_user, browser)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertTrue(dossier_email)
        self.assertEqual(200, browser.status_code)

        documents = [self.mail_eml, self.mail_msg]

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)

        self.assertIsNotNone(oc_url)
        self.assertEqual(200, browser.status_code)

        expected_token = {
            u"action": u"attach",
            u"bcc": u"1014013300@example.org",
            u"documents": [u"createemails00000000000000000001", u"createemails00000000000000000002"],
            u"exp": 4121033100,
            u"sub": u"kathi.barfuss",
            u"url": u"http://nohost/plone/oc_attach",
        }
        raw_token = oc_url.split(":")[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)

        self.assertItemsEqual(token.pop('documents'), expected_token.pop('documents'))
        self.assertEqual(expected_token, token)

        expected_payloads = [
            {
                u"bcc": u"1014013300@example.org",
                u"content-type": u"message/rfc822",
                u"csrf-token": u"86ecf9b4135514f8c94c61ce336a4b98b4aaed8a",
                u"document-url": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/"
                                 u"document-29",
                u"download": u"download",
                u"filename": u"Die Buergschaft.eml",
                u"title": u"Die B\xfcrgschaft",
                u"uuid": u"createemails00000000000000000001",
                u'version': 0,
            },
            {
                u"bcc": u"1014013300@example.org",
                u"content-type": u"application/vnd.ms-outlook",
                u"csrf-token": u"86ecf9b4135514f8c94c61ce336a4b98b4aaed8a",
                u"document-url": u"http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/"
                                 u"document-30",
                u"download": u"@@download/original_message",
                u"filename": u"No Subject.msg",
                u"title": u"[No Subject]",
                u"uuid": u"createemails00000000000000000002",
                u'version': 0,
            },
        ]

        self.assertItemsEqual(expected_payloads, payloads)

    @browsing
    def test_attach_to_email_from_different_parents(self, browser):
        self.login(self.regular_user, browser)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertTrue(dossier_email)
        self.assertEqual(200, browser.status_code)

        documents = [self.document, self.subdocument]

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_dossier_multiattach_oc_url(browser, self.dossier, documents, dossier_email)

        self.assertIsNotNone(oc_url)
        self.assertEqual(200, browser.status_code)

        expected_token = {
            u"action": u"attach",
            u"bcc": u"1014013300@example.org",
            u"documents": [u"createtreatydossiers000000000002", u"createtreatydossiers000000000017"],
            u"exp": 4121033100,
            u"sub": u"kathi.barfuss",
            u"url": u"http://nohost/plone/oc_attach",
        }
        raw_token = oc_url.split(":")[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)

        self.assertItemsEqual(token.pop('documents'), expected_token.pop('documents'))
        self.assertEqual(expected_token, token)

        expected_payloads = [
            {
                u'bcc': u'1014173300@example.org',
                u'content-type': u'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-22',
                u'download': u'download',
                u'filename': u'Uebersicht der Vertraege von 2016.xlsx',
                u'title': u'\xdcbersicht der Vertr\xe4ge von 2016',
                u'uuid': u'createtreatydossiers000000000017',
                u'version': None
            },
            {
                u'bcc': u'1014013300@example.org',
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
                u'download': u'download',
                u'filename': u'Vertraegsentwurf.docx',
                u'title': u'Vertr\xe4gsentwurf',
                u'uuid': u'createtreatydossiers000000000002',
                u'version': None
            }
        ]

        self.assertItemsEqual(expected_payloads, payloads)

    @browsing
    def test_checkout_checkin(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.mail_eml)
            self.assertIsNone(oc_url)


class TestOfficeconnectorMailAPIWithAttachInTeamraum(OCSolrIntegrationTestCase):

    features = ('!officeconnector-checkout', 'officeconnector-attach', 'workspace')

    @browsing
    def test_attach_to_email(self, browser):
        self.login(self.workspace_member, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.workspace_document)

        self.assertIsNotNone(oc_url)
        self.assertEqual(200, browser.status_code)

        expected_token = {
            u"action": u"attach",
            u"documents": [u"createworkspace00000000000000003"],
            u"exp": 4121033100,
            u"sub": u"beatrice.schrodinger",
            u"url": u"http://nohost/plone/oc_attach",
        }
        raw_token = oc_url.split(":")[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))

        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u"bcc": u"1018013300@example.org",
            u"content-type": u"text/plain",
            u"csrf-token": u"86ecf9b4135514f8c94c61ce336a4b98b4aaed8a",
            u"document-url": u"http://nohost/plone/workspaces/workspace-1/document-38",
            u"download": u"download",
            u"filename": u"Teamraumdokument.txt",
            u"title": u"Teamraumdokument",
            u"uuid": u"createworkspace00000000000000003",
            u'version': None,
        }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(expected_payloads, payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEqual(file_contents, self.workspace_document.get_file().data)
