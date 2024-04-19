from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCSolrIntegrationTestCase
from plone.uuid.interfaces import IUUID
from zExceptions import Forbidden
import json
import jwt


class TestOfficeconnectorDossierAPIWithAttach(OCSolrIntegrationTestCase):

    features = (
        '!officeconnector-checkout',
        'officeconnector-attach',
    )

    @browsing
    def test_attach_to_email_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_mail_sets_flags(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document,
            headers=self.api_headers,
            view='officeconnector_attach_url?attach=false&links=true&set_bcc=false',
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(u'-attach,-bcc', token['flags'])

    @browsing
    def test_attach_to_mail_does_not_set_flags(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document,
            headers=self.api_headers,
            view='officeconnector_attach_url',
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertIsNone(token.get('flags'))

    @browsing
    def test_attach_to_mail_sets_attach_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document,
            headers=self.api_headers,
            view='officeconnector_attach_url?attach=false',
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(u'-attach', token['flags'])

    @browsing
    def test_attach_to_mail_does_not_set_attach_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document,
            headers=self.api_headers,
            view='officeconnector_attach_url?attach=true',
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertIsNone(token.get('flags'))

    @browsing
    def test_attach_to_mail_sets_bcc_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document,
            headers=self.api_headers,
            view='officeconnector_attach_url?set_bcc=false',
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(u'-bcc', token['flags'])

    @browsing
    def test_attach_to_mail_does_not_set_bcc_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document,
            headers=self.api_headers,
            view='officeconnector_attach_url?set_bcc=true',
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertIsNone(token.get('flags'))

    @browsing
    def test_attach_to_mail_sets_links_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document,
            headers=self.api_headers,
            view='officeconnector_attach_url?links=false',
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(u'-links', token['flags'])

    @browsing
    def test_attach_to_mail_does_not_set_links_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document,
            headers=self.api_headers,
            view='officeconnector_attach_url?links=true',
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertIsNone(token.get('flags'))

    @browsing
    def test_attach_to_email_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': self.regular_user.id,
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'bcc': u'1014013300@example.org',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
            u'download': u'download',
            u'filename': u'Vertraegsentwurf.docx',
            u'title': u'Vertr\xe4gsentwurf',
            u'uuid': u'createtreatydossiers000000000002',
            u'version': None,
            }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        self.assertEqual(payloads, expected_payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEquals(file_contents, self.document.file.data)

    @browsing
    def test_attach_to_email_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.inactive_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.inactive_document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createinactivedossier00000000002'],
            u'exp': 4121033100,
            u'sub': self.regular_user.id,
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'content-type': u'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-6/document-27',
            u'download': u'download',
            u'filename': u'Uebersicht der Inaktiven Vertraege von 2016.xlsx',
            u'title': u'\xdcbersicht der Inaktiven Vertr\xe4ge von 2016',
            u'uuid': u'createinactivedossier00000000002',
            u'version': None,
            }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        self.assertEqual(payloads, expected_payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEquals(file_contents, self.inactive_document.file.data)

    @browsing
    def test_attach_to_email_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_attach_oc_url(browser, self.expired_document)

            self.assertIsNone(oc_url)

    @browsing
    def test_attach_to_email_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_attach_oc_url(browser, self.expired_document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createexpireddossier000000000002'],
            u'exp': 4121033100,
            u'sub': self.regular_user.id,
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'content-type': u'application/msword',
            u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-5/document-26',
            u'download': u'download',
            u'filename': u'Uebersicht der Vertraege vor 2000.doc',
            u'title': u'\xdcbersicht der Vertr\xe4ge vor 2000',
            u'uuid': u'createexpireddossier000000000002',
            u'version': None,
            }]
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        self.assertEqual(payloads, expected_payloads)

        file_contents = self.download_document(browser, raw_token, payloads[0])
        self.assertEquals(file_contents, self.expired_document.file.data)

    @browsing
    def test_attach_many_to_email_open(self, browser):
        self.login(self.regular_user, browser)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertTrue(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            self.document,
            self.taskdocument,
            ]

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'bcc': u'1014013300@example.org',
            u'documents': [u'createtreatydossiers000000000002', u'createtasks000000000000000000003'],
            u'exp': 4121033100,
            u'sub': self.regular_user.id,
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)

        self.assertItemsEqual(token.pop('documents'), expected_token.pop('documents'))
        self.assertEqual(expected_token, token)

        expected_payloads = [
            {
                u'bcc': u'1014013300@example.org',
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/document-14',
                u'download': u'download',
                u'filename': u'Vertraegsentwurf.docx',
                u'title': u'Vertr\xe4gsentwurf',
                u'uuid': u'createtreatydossiers000000000002',
                u'version': None,
                },
            {
                u'bcc': u'1014013300@example.org',
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/task-1/document-35',
                u'download': u'download',
                u'filename': u'Feedback zum Vertragsentwurf.docx',
                u'title': u'Feedback zum Vertragsentwurf',
                u'uuid': u'createtasks000000000000000000003',
                u'version': None,
                },
            ]
        self.assertItemsEqual(payloads, expected_payloads)

    @browsing
    def test_attach_many_to_email_inactive(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertFalse(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            self.document,
            self.taskdocument,
            ]

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createtreatydossiers000000000002', u'createtasks000000000000000000003'],
            u'exp': 4121033100,
            u'sub': self.regular_user.id,
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)

        self.assertItemsEqual(token.pop('documents'), expected_token.pop('documents'))
        self.assertEqual(expected_token, token)

        expected_payloads = [
            {
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/document-14',
                u'download': u'download',
                u'filename': u'Vertraegsentwurf.docx',
                u'title': u'Vertr\xe4gsentwurf',
                u'uuid': u'createtreatydossiers000000000002',
                u'version': None,
                },
            {
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/task-1/document-35',
                u'download': u'download',
                u'filename': u'Feedback zum Vertragsentwurf.docx',
                u'title': u'Feedback zum Vertragsentwurf',
                u'uuid': u'createtasks000000000000000000003',
                u'version': None,
                },
            ]
        self.assertItemsEqual(payloads, expected_payloads)

    @browsing
    def test_attach_many_to_email_resolved(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        dossier_email = self.fetch_dossier_bcc(browser, self.dossier)

        self.assertFalse(dossier_email)
        self.assertEquals(200, browser.status_code)

        documents = [
            self.document,
            self.taskdocument,
            ]

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_dossier_multiattach_oc_url(
                browser,
                self.dossier,
                documents,
                dossier_email,
                )

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'attach',
            u'documents': [u'createtreatydossiers000000000002', u'createtasks000000000000000000003'],
            u'exp': 4121033100,
            u'sub': self.regular_user.id,
            u'url': u'http://nohost/plone/oc_attach',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        payloads = self.fetch_document_attach_payloads(browser, raw_token, token)

        self.assertItemsEqual(token.pop('documents'), expected_token.pop('documents'))
        self.assertEqual(expected_token, token)

        expected_payloads = [
            {
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/document-14',
                u'download': u'download',
                u'filename': u'Vertraegsentwurf.docx',
                u'title': u'Vertr\xe4gsentwurf',
                u'uuid': u'createtreatydossiers000000000002',
                u'version': None,
                },
            {
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'csrf-token': u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                                 u'dossier-1/task-1/document-35',
                u'download': u'download',
                u'filename': u'Feedback zum Vertragsentwurf.docx',
                u'title': u'Feedback zum Vertragsentwurf',
                u'uuid': u'createtasks000000000000000000003',
                u'version': None,
                },
            ]
        self.assertItemsEqual(payloads, expected_payloads)

    @browsing
    def test_attach_multiple_documents_sets_flags(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal,
            method='POST',
            headers=self.api_headers,
            view='officeconnector_attach_url',
            data=json.dumps({'documents': ['/'.join(self.document.getPhysicalPath())],
                             'attach': True, 'links': False, 'set_bcc': False})
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(u'-links,-bcc', token['flags'])

    @browsing
    def test_attach_multiple_documents_does_not_set_flags(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal,
            method='POST',
            headers=self.api_headers,
            view='officeconnector_attach_url',
            data=json.dumps({'documents': ['/'.join(self.document.getPhysicalPath())]})
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertIsNone(token.get('flags'))

    @browsing
    def test_attach_multiple_documents_sets_attach_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal,
            method='POST',
            headers=self.api_headers,
            view='officeconnector_attach_url',
            data=json.dumps({'documents': ['/'.join(self.document.getPhysicalPath())],
                             'attach': False})
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(u'-attach', token['flags'])

    @browsing
    def test_attach_multiple_documents_does_not_set_attach_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal,
            method='POST',
            headers=self.api_headers,
            view='officeconnector_attach_url',
            data=json.dumps({'documents': ['/'.join(self.document.getPhysicalPath())],
                             'attach': True})
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertIsNone(token.get('flags'))

    @browsing
    def test_attach_multiple_documents_sets_bcc_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal,
            method='POST',
            headers=self.api_headers,
            view='officeconnector_attach_url',
            data=json.dumps({'documents': ['/'.join(self.document.getPhysicalPath())],
                             'set_bcc': False})
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(u'-bcc', token['flags'])

    @browsing
    def test_attach_multiple_documents_does_not_set_bcc_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal,
            method='POST',
            headers=self.api_headers,
            view='officeconnector_attach_url',
            data=json.dumps({'documents': ['/'.join(self.document.getPhysicalPath())],
                             'set_bcc': True})
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertIsNone(token.get('flags'))

    @browsing
    def test_attach_multiple_documents_sets_links_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal,
            method='POST',
            headers=self.api_headers,
            view='officeconnector_attach_url',
            data=json.dumps({'documents': ['/'.join(self.document.getPhysicalPath())],
                             'links': False})
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(u'-links', token['flags'])

    @browsing
    def test_attach_multiple_documents_works_for_external_user(self, browser):
        external_user = create(Builder('user').with_userid('external.user').with_roles([]))
        create(Builder('ogds_user').id('external.user'))

        with self.login(self.administrator):
            self.meeting_dossier.__ac_local_roles_block__ = True
            self.set_roles(self.leaf_repofolder, 'external.user', ['Reader'])
            docs =['/'.join(doc.getPhysicalPath()) for doc
                   in [self.document, self.empty_document, self.mail_eml, self.meeting_document]]
            segments = list(self.subdocument.getPhysicalPath())
            segments.remove('plone')
            docs.append('/'.join(segments))
            data =  json.dumps({'documents': docs})

        self.login(external_user, browser)
        browser.open(
            self.portal,
            method='POST',
            headers=self.api_headers,
            view='officeconnector_attach_url',
            data=data
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        with self.login(self.regular_user):
            self.assertItemsEqual(
                [IUUID(self.document), IUUID(self.subdocument), IUUID(self.mail_eml)],
                token['documents'])

    @browsing
    def test_attach_multiple_documents_does_not_set_links_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.portal,
            method='POST',
            headers=self.api_headers,
            view='officeconnector_attach_url',
            data=json.dumps({'documents': ['/'.join(self.document.getPhysicalPath())],
                             'links': True})
        )
        url = browser.json['url']
        raw_token = url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertIsNone(token.get('flags'))

    @browsing
    def test_checkout_checkin_open_without_file(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_open_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_inactive_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.inactive_document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.inactive_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_inactive_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.inactive_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_without_file(self, browser):
        self.login(self.regular_user, browser)
        self.expired_document.file = None

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.expired_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_checkout_checkin_resolved_with_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(401):
            oc_url = self.fetch_document_checkout_oc_url(
                browser,
                self.expired_document,
                )

            self.assertIsNone(oc_url)

    @browsing
    def test_guest_cannot_attach_document_in_a_restricted_workspace(self, browser):
        with self.login(self.workspace_admin):
            self.workspace.restrict_downloading_documents = True

        self.login(self.workspace_guest, browser)
        browser.exception_bubbling = True

        with self.assertRaises(Forbidden):
            browser.open(
                self.workspace_document,
                headers=self.api_headers,
                view='officeconnector_attach_url',
            )

    @browsing
    def test_guest_can_attach_document_in_a_restricted_workspace(self, browser):
        self.login(self.workspace_guest, browser)
        browser.exception_bubbling = True

        browser.open(
            self.workspace_document,
            headers=self.api_headers,
            view='officeconnector_attach_url',
        )
        self.assertEqual(200, browser.status_code)
