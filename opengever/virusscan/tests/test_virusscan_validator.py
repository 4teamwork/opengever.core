from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.dexterity import erroneous_fields
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import IntegrationTestCase
from opengever.virusscan.interfaces import IAVScannerSettings
from opengever.virusscan.testing import EICAR
from opengever.virusscan.testing import register_mock_av_scanner
from plone import api
import json


class TestVirusScanValidator(IntegrationTestCase):

    def setUp(self):
        super(TestVirusScanValidator, self).setUp()
        register_mock_av_scanner()
        api.portal.set_registry_record(
            'scan_before_upload', True, interface=IAVScannerSettings)
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
            {'File': ['Validation failed, file is virus-infected. (Eicar-Test-Signature FOUND)']},
            erroneous_fields())
        self.assertEqual(0, len(self.empty_dossier.contentItems()))

        browser.fill({'File': ("No virus", 'file.txt', 'text/plain')}).save()
        self.assertEqual([], error_messages())
        self.assertEqual(1, len(self.empty_dossier.contentItems()))

    @browsing
    def test_document_add_form_does_not_scan_file_field_for_viruses_when_disabled(self, browser):
        api.portal.set_registry_record(
            'scan_before_upload', False, interface=IAVScannerSettings)

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
            {'Archival file': ['Validation failed, file is virus-infected. (Eicar-Test-Signature FOUND)']},
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
            {'File': ['Validation failed, file is virus-infected. (Eicar-Test-Signature FOUND)']},
            erroneous_fields())
        self.assertIsNone(self.empty_document.get_file())

        browser.open(self.empty_document, view='edit')
        browser.fill({'File': ("No virus", 'file.txt', 'text/plain')}).save()
        self.assertEqual([], error_messages())
        self.assertIsNotNone(self.empty_document.get_file())

    @browsing
    def test_document_edit_form_does_not_scan_file_field_for_viruses_when_disabled(self, browser):
        api.portal.set_registry_record(
            'scan_before_upload', False, interface=IAVScannerSettings)

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
            {'Archival file': ['Validation failed, file is virus-infected. (Eicar-Test-Signature FOUND)']},
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
             u'Validation failed, file is virus-infected. (Eicar-Test-Signature FOUND)',
             result['error'])

        result = factory(filename='file.txt',
                         title=None,  # ignored by adapter
                         description=None,  # ignored by adapter
                         content_type='text/plain',
                         data='No virus',
                         portal_type='opengever.document.document')

        self.assertIsNotNone(result['success'])
        self.assertEqual('No virus', result['success'].file.data)

    @browsing
    def test_document_post_scans_file_for_viruses_when_enabled(self, browser):
        self.login(self.regular_user, browser)

        with self.observe_children(self.empty_dossier) as children,\
                browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'@type': 'opengever.document.document',
                    'file': {'data': EICAR, 'filename': 'file.txt'}}
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(0, len(children['added']))
        self.assertEqual(
            u"[{'message': 'Validation failed, file is virus-infected. "
            u"(Eicar-Test-Signature FOUND)', 'error': 'ValidationError'}]",
            browser.json['message'])

        data['file']['data'] = "No virus"
        with self.observe_children(self.empty_dossier) as children:
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)
        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))

    @browsing
    def test_document_post_does_not_scan_file_for_viruses_when_disabled(self, browser):
        api.portal.set_registry_record(
            'scan_before_upload', False, interface=IAVScannerSettings)
        self.login(self.regular_user, browser)

        with self.observe_children(self.empty_dossier) as children:
            data = {'@type': 'opengever.document.document',
                    'file': {'data': EICAR, 'filename': 'file.txt'}}
            browser.open(self.empty_dossier, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))

    @browsing
    def test_document_patch_scans_file_for_viruses_when_enabled(self, browser):
        self.login(self.regular_user, browser)
        self.get_checkout_manager(self.document).checkout()

        with browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'file': {'data': EICAR, 'filename': 'file.txt'}}
            browser.open(self.document, data=json.dumps(data),
                         method='PATCH', headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            u"[{'message': 'Validation failed, file is virus-infected. "
            u"(Eicar-Test-Signature FOUND)', 'error': 'ValidationError'}]",
            browser.json['message'])

        data['file']['data'] = "No virus"
        browser.open(self.document, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)