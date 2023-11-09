from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.interfaces import IEmailAddress
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.dexterity import erroneous_fields
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.versioner import Versioner
from opengever.mail.tests import MAIL_DATA
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing.assets import load
from opengever.virusscan.interfaces import IAVScannerSettings
from opengever.virusscan.testing import EICAR
from opengever.virusscan.testing import EICAR_MAIL_TEMPLATE
from opengever.virusscan.testing import register_mock_av_scanner
from plone import api
from zope.component import getMultiAdapter
import base64
import json
import transaction


class TestVirusScanValidator(IntegrationTestCase):

    def setUp(self):
        super(TestVirusScanValidator, self).setUp()
        register_mock_av_scanner()
        api.portal.set_registry_record(
            'scan_on_upload', True, interface=IAVScannerSettings)
        api.portal.set_registry_record(
            'scan_before_download', True, interface=IAVScannerSettings)

    @browsing
    def test_document_add_form_scans_file_field_for_viruses_when_enabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.empty_dossier)
        factoriesmenu.add('Document')
        browser.fill({'Title': u'My Document',
                      'File': (EICAR, 'file.txt', 'text/plain')}).save()

        self.assertEqual(["There were some errors."], error_messages())
        self.assertEqual(
            {'File': ['Error - Virus detected!']},
            erroneous_fields())
        self.assertEqual(0, len(self.empty_dossier.contentItems()))

        browser.fill({'File': ("No virus", 'file.txt', 'text/plain')}).save()
        self.assertEqual([], error_messages())
        self.assertEqual(1, len(self.empty_dossier.contentItems()))

    @browsing
    def test_document_add_form_does_not_scan_file_field_for_viruses_when_disabled(self, browser):
        api.portal.set_registry_record(
            'scan_on_upload', False, interface=IAVScannerSettings)

        self.login(self.regular_user, browser)
        browser.open(self.empty_dossier)
        factoriesmenu.add('Document')
        browser.fill({'Title': u'My Document',
                      'File': (EICAR, 'file.txt', 'text/plain')}).save()

        self.assertEqual([], error_messages())
        self.assertEqual(1, len(self.empty_dossier.contentItems()))

    @browsing
    def test_document_add_form_scans_archival_file_field_for_viruses_when_enabled(self, browser):
        self.login(self.manager, browser)
        browser.open(self.empty_dossier)
        factoriesmenu.add('Document')
        browser.fill({'Title': u'My Document',
                      'File': ('no virus', 'file.txt', 'text/plain'),
                      'Archival file': (EICAR, 'archival_file.txt', 'text/plain')}).save()

        self.assertEqual(["There were some errors."], error_messages())
        self.assertEqual(
            {'Archival file': ['Error - Virus detected!']},
            erroneous_fields())
        self.assertEqual(0, len(self.empty_dossier.contentItems()))

        browser.fill({'Archival file': ("No virus", 'archival_file.txt', 'text/plain')}).save()
        self.assertEqual([], error_messages())
        self.assertEqual(1, len(self.empty_dossier.contentItems()))

    @browsing
    def test_document_edit_form_scans_file_field_for_viruses_when_enabled(self, browser):
        self.login(self.regular_user, browser)
        self.get_checkout_manager(self.empty_document).checkout()

        browser.open(self.empty_document, view='edit')
        browser.fill({'File': (EICAR, 'file.txt', 'text/plain')}).save()
        self.assertEqual(["There were some errors."], error_messages())
        self.assertEqual(
            {'File': ['Error - Virus detected!']},
            erroneous_fields())
        self.assertIsNone(self.empty_document.get_file())

        browser.open(self.empty_document, view='edit')
        browser.fill({'File': ("No virus", 'file.txt', 'text/plain')}).save()
        self.assertEqual([], error_messages())
        self.assertIsNotNone(self.empty_document.get_file())

    @browsing
    def test_document_edit_form_does_not_scan_file_field_for_viruses_when_disabled(self, browser):
        api.portal.set_registry_record(
            'scan_on_upload', False, interface=IAVScannerSettings)

        self.login(self.regular_user, browser)
        self.get_checkout_manager(self.document).checkout()
        browser.open(self.empty_document, view='edit')
        browser.fill({'File': (EICAR, 'file.txt', 'text/plain')}).save()

        self.assertEqual([], error_messages())
        self.assertIsNotNone(self.empty_document.get_file())

    @browsing
    def test_document_edit_form_scans_archival_file_field_for_viruses_when_enabled(self, browser):
        self.login(self.manager, browser)
        browser.open(self.document, view='edit')
        browser.fill({'Archival file': (EICAR, 'file.txt', 'text/plain')}).save()
        self.assertEqual(["There were some errors."], error_messages())
        self.assertEqual(
            {'Archival file': ['Error - Virus detected!']},
            erroneous_fields())
        self.assertIsNone(self.document.archival_file)

        browser.open(self.document, view='edit')
        browser.fill({'Archival file': ("No virus", 'file.txt', 'text/plain')}).save()
        self.assertEqual([], error_messages())
        self.assertIsNotNone(self.document.archival_file)

    def test_quickupload_scans_file_for_viruses_when_enabled(self):
        self.login(self.regular_user)
        factory = IQuickUploadFileFactory(self.dossier)
        result = factory(filename='file.txt',
                         title=None,  # ignored by adapter
                         description=None,  # ignored by adapter
                         content_type='text/plain',
                         data=EICAR,
                         portal_type='opengever.document.document')

        self.assertIsNone(result['success'])
        self.assertEqual(
             u'Error - Virus detected!',
             result['error'])

        result = factory(filename=u'f\xefle.txt',
                         title=None,  # ignored by adapter
                         description=None,  # ignored by adapter
                         content_type='text/plain',
                         data='No virus',
                         portal_type='opengever.document.document')

        self.assertIsNotNone(result['success'])
        self.assertEqual('No virus', result['success'].file.data)

    def test_quickupload_scans_mail_for_viruses_when_enabled(self):
        self.login(self.regular_user)
        factory = IQuickUploadFileFactory(self.dossier)
        result = factory(filename=u'f\xefle.eml',
                         title=None,  # ignored by adapter
                         description=None,  # ignored by adapter
                         content_type='message/rfc822',
                         data=EICAR,
                         portal_type='ftw.mail.mail')

        self.assertIsNone(result['success'])
        self.assertEqual(
             u'Error - Virus detected!',
             result['error'])

        result = factory(filename=u'f\xefle.eml',
                         title=None,  # ignored by adapter
                         description=None,  # ignored by adapter
                         content_type='message/rfc822',
                         data=MAIL_DATA,
                         portal_type='ftw.mail.mail')

        self.assertIsNotNone(result['success'])
        self.assertEqual(MAIL_DATA, result['success'].message.data)

    @browsing
    def test_document_post_scans_file_for_viruses_when_enabled(self, browser):
        self.login(self.regular_user, browser)

        with self.observe_children(self.empty_dossier) as children,\
                browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'@type': 'opengever.document.document',
                    'file': {'data': EICAR, 'filename': u'f\xefle.txt'}}
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(0, len(children['added']))
        self.assertEqual(u'Error - Virus detected!',
                         browser.json['translated_message'])

        data['file']['data'] = "No virus"
        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)
        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))

    @browsing
    def test_document_post_does_not_scan_file_for_viruses_when_disabled(self, browser):
        api.portal.set_registry_record(
            'scan_on_upload', False, interface=IAVScannerSettings)
        self.login(self.regular_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            data = {'@type': 'opengever.document.document',
                    'file': {'data': EICAR, 'filename': u'f\xefle.txt'}}
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))

    @browsing
    def test_document_patch_scans_file_for_viruses_when_enabled(self, browser):
        self.login(self.regular_user, browser)
        self.get_checkout_manager(self.document).checkout()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'file': {'data': EICAR, 'filename': u'f\xefle.txt'}}
            browser.open(self.document, data=json.dumps(data),
                         method='PATCH', headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(u'Error - Virus detected!',
                         browser.json['translated_message'])

        data['file']['data'] = "No virus"
        browser.open(self.document, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)

    @browsing
    def test_document_post_scans_archival_file_for_viruses_when_enabled(self, browser):
        self.login(self.manager, browser)

        with self.observe_children(self.empty_dossier) as children,\
                browser.expect_http_error(code=400):
            data = {'@type': 'opengever.document.document',
                    'file': {'data': "No virus", 'filename': u'f\xefle.txt'},
                    'archival_file': {'data': EICAR, 'filename': u'f\xefle.txt'}}
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(0, len(children['added']))
        self.assertEqual(u'Error - Virus detected!',
                         browser.json['translated_message'])

        data['archival_file']['data'] = "No virus"
        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)
        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))

    @browsing
    def test_document_post_does_not_scan_archival_file_for_viruses_when_disabled(self, browser):
        self.login(self.manager, browser)
        api.portal.set_registry_record(
            'scan_on_upload', False, interface=IAVScannerSettings)

        with self.observe_children(self.empty_dossier) as children:
            data = {'@type': 'opengever.document.document',
                    'file': {'data': "No virus", 'filename': u'f\xefle.txt'},
                    'archival_file': {'data': EICAR, 'filename': u'f\xefle.txt'}}
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))

    @browsing
    def test_mail_eml_post_scans_message_for_viruses_when_enabled(self, browser):
        self.login(self.regular_user, browser)

        with self.observe_children(self.empty_dossier) as children,\
                browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'@type': 'ftw.mail.mail',
                    'message': {'data': EICAR, 'filename': u'ma\xefl.eml'}}
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(0, len(children['added']))
        self.assertEqual(
            {u'type': u'BadRequest',
             u'additional_metadata': {},
             u'translated_message': u'Error - Virus detected!',
             u'message': u"[{'message': u'file_infected', 'error': 'ValidationError'}]"},
            browser.json)

        data['message']['data'] = "No virus"
        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)
        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))

    @browsing
    def test_mail_msg_post_scans_message_for_viruses_when_enabled(self, browser):
        self.login(self.regular_user, browser)

        with self.observe_children(self.empty_dossier) as children,\
                browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'@type': 'ftw.mail.mail',
                    'message': {'data': EICAR, 'filename': u'ma\xefl.msg'}}
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(0, len(children['added']))
        self.assertEqual(
            {u'type': u'BadRequest',
             u'additional_metadata': {},
             u'translated_message': u'Error - Virus detected!',
             u'message': u"[{'message': u'file_infected', 'error': 'ValidationError'}]"},
            browser.json)

        msg = base64.b64encode(load('testmail.msg'))
        data['message']['data'] = msg
        data['message']['encoding'] = "base64"

        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)
        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))

    def test_inbound_mail_scans_for_virus_when_enabled(self):
        self.login(self.regular_user)
        mail_to = IEmailAddress(self.request).get_email_for_object(self.empty_dossier)
        mail_from = self.regular_user.getProperty('email')
        mail = EICAR_MAIL_TEMPLATE.format(
            from_address=mail_from, to_address=mail_to)

        with self.observe_children(self.empty_dossier) as children:
            self.request.set('mail', mail)
            view = getMultiAdapter((self.portal, self.request), name='mail-inbound')
            self.assertEquals('65:file_infected', view())
        self.assertEqual(0, len(children['added']))

        api.portal.set_registry_record('scan_on_upload', False, interface=IAVScannerSettings)
        with self.observe_children(self.empty_dossier) as children:
            self.assertEquals('0:OK', view())
        self.assertEqual(1, len(children['added']))


class TestVirusScanDownloadValidator(IntegrationTestCase):

    headers = {
        'Accept': 'application/json',
    }

    def setUp(self):
        super(TestVirusScanDownloadValidator, self).setUp()
        register_mock_av_scanner()
        api.portal.set_registry_record(
            'scan_before_download', True, interface=IAVScannerSettings)
        with self.login(self.regular_user):
            self.document.file.data = EICAR
            self.subdocument.file.data = "No virus"

    @browsing
    def test_download_view_scans_file_if_enabled(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='download?error_as_message=1')
        self.assertEqual(
            ['Error - Virus detected!'],
            error_messages())
        self.assertEqual('text/html;charset=utf-8',
                         browser.headers['content-type'])
        self.assertIsNone(browser.headers.get('content-disposition'))

        browser.open(self.subdocument, view='download')
        self.assertEqual(
            'attachment; filename="Uebersicht der Vertraege von 2016.xlsx"',
            browser.headers.get('content-disposition'))
        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            browser.headers['content-type'])
        self.assertEqual("No virus", browser.contents)

    @browsing
    def test_download_view_scans_mail_if_enabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, view='download?error_as_message=1')
        self.assertEqual(
            'attachment; filename="Die Buergschaft.eml"',
            browser.headers.get('content-disposition'))
        self.assertEqual(
            'message/rfc822',
            browser.headers['content-type'])

        self.mail_eml.message.data = EICAR
        browser.open(self.mail_eml, view='download?error_as_message=1')
        self.assertEqual(
            ['Error - Virus detected!'],
            error_messages())
        self.assertEqual('text/html;charset=utf-8',
                         browser.headers['content-type'])
        self.assertIsNone(browser.headers.get('content-disposition'))

    @browsing
    def test_download_view_does_not_scan_file_if_disabled(self, browser):
        api.portal.set_registry_record(
            'scan_before_download', False, interface=IAVScannerSettings)

        self.login(self.regular_user, browser)
        browser.open(self.document, view='download?error_as_message=1')
        self.assertEqual(
            'attachment; filename="Vertraegsentwurf.docx"',
            browser.headers.get('content-disposition'))
        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            browser.headers['content-type'])
        self.assertEqual(EICAR, browser.contents)

    @browsing
    def test_download_view_scans_file_from_edit_view(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)
        browser.open(self.document, view='edit')
        browser.click_on("Vertraegsentwurf.docx")
        browser.click_on("Download")

        self.assertEqual(
            ['Error - Virus detected!'],
            error_messages())
        self.assertEqual('text/html;charset=utf-8',
                         browser.headers['content-type'])
        self.assertIsNone(browser.headers.get('content-disposition'))
        self.assertEqual(self.document.absolute_url(), browser.url)

        self.checkout_document(self.subdocument)
        browser.open(self.subdocument, view='edit')
        browser.click_on("Uebersicht der Vertraege von 2016.xlsx")
        browser.click_on("Download")
        self.assertEqual(
            'attachment; filename="Uebersicht der Vertraege von 2016.xlsx"',
            browser.headers.get('content-disposition'))
        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            browser.headers['content-type'])
        self.assertEqual("No virus", browser.contents)

    @browsing
    def test_download_archival_file_from_edit_view_scans_for_virus(self, browser):
        self.login(self.manager, browser)

        ArchivalFileConverter(self.document).store_file(EICAR)
        browser.open(self.document, view='edit')
        browser.click_on("Vertraegsentwurf.pdf")

        self.assertEqual(
            ['Error - Virus detected!'],
            error_messages())
        self.assertEqual('text/html;charset=utf-8',
                         browser.headers['content-type'])
        self.assertIsNone(browser.headers.get('content-disposition'))
        self.assertEqual(self.document.absolute_url(), browser.url)

        ArchivalFileConverter(self.document).store_file("No virus")
        browser.open(self.document, view='edit')
        browser.click_on("Vertraegsentwurf.pdf")

        self.assertEqual(
            "attachment; filename*=UTF-8''Vertraegsentwurf.pdf",
            browser.headers.get('content-disposition'))
        self.assertEqual(
            'application/pdf',
            browser.headers['content-type'])
        self.assertEqual("No virus", browser.contents)

    @browsing
    def test_download_over_api_scans_file_if_enabled(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=400):
            browser.open(self.document, view='download', headers=self.api_headers)

        self.assertEqual(
            u'file_infected',
            browser.json['message'])

        browser.open(self.subdocument, view='download')
        self.assertEqual(
            'attachment; filename="Uebersicht der Vertraege von 2016.xlsx"',
            browser.headers.get('content-disposition'))
        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            browser.headers['content-type'])
        self.assertEqual("No virus", browser.contents)

    @browsing
    def test_download_over_api_scans_mail_if_enabled(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.mail_eml, view='download')
        self.assertEqual(
            'attachment; filename="Die Buergschaft.eml"',
            browser.headers.get('content-disposition'))
        self.assertEqual(
            'message/rfc822',
            browser.headers['content-type'])

        self.mail_eml.message.data = EICAR
        with browser.expect_http_error(code=400):
            browser.open(self.mail_eml, view='download', headers=self.headers)

        self.assertEqual(
            u'file_infected',
            browser.json['message'])

    @browsing
    def test_download_versioned_copy_scans_file_if_enabled(self, browser):
        self.login(self.regular_user, browser)
        Versioner(self.document).create_version('Initial version')
        browser.open(self.document, view='tabbedview_view-versions')
        browser.css('a.function-download-copy').first.click()
        browser.find('Download').click()
        self.assertEqual(
            ['Error - Virus detected!'],
            error_messages())
        self.assertEqual('text/html;charset=utf-8',
                         browser.headers['content-type'])
        self.assertIsNone(browser.headers.get('content-disposition'))
        self.assertEqual(self.document.absolute_url(), browser.url)

    @browsing
    def test_download_versioned_copy_over_api_scans_file_if_enabled(self, browser):
        self.login(self.regular_user, browser)
        Versioner(self.document).create_version('Initial version')

        with browser.expect_http_error(code=400):
            browser.open(self.document,
                         view='download_file_version',
                         data={'version_id': 0},
                         headers=self.headers)
        self.assertEqual(
            u'file_infected',
            browser.json['message'])


class TestVirusScanDownloadValidatorFunctional(FunctionalTestCase):
    """We need a functional test to be able to commit the blob."""

    def setUp(self):
        super(TestVirusScanDownloadValidatorFunctional, self).setUp()
        register_mock_av_scanner()
        api.portal.set_registry_record(
            'scan_before_download', True, interface=IAVScannerSettings)

    headers = {
        'Accept': 'application/json',
    }

    @browsing
    def test_download_versioned_copy_over_api_with_virusscan_enabled(self, browser):
        self.login()
        document = create(Builder('document').with_dummy_content())
        Versioner(document).create_version('Initial version')
        transaction.commit()

        browser.login().open(document,
                             view='download_file_version',
                             data={'version_id': 0},
                             headers={'Accept': 'application/json'})
        self.assertEqual(
            'attachment; filename="Testdokumaent.doc"',
            browser.headers.get('content-disposition'))
        self.assertEqual(
            'application/msword',
            browser.headers['content-type'])
        self.assertEqual("Test data", browser.contents)
