from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from plone import api
from plone.uuid.interfaces import IUUID
from requests_toolbelt.multipart.encoder import MultipartEncoder


class TestScanIn(IntegrationTestCase):

    def create_single_inbox(self):
        inbox = create(Builder('inbox').titled(u'Inbox'))
        RoleAssignmentManager(inbox).add_or_update_assignment(
            SharingRoleAssignment(self.regular_user.getId(),
                                  ['Reader', 'Contributor', 'Editor']))
        return inbox

    def create_org_unit_inbox(self):
        container = create(Builder('inbox_container').titled(u'Inboxes'))
        RoleAssignmentManager(container).add_or_update_assignment(
            SharingRoleAssignment(self.regular_user.getId(),
                                  ['Reader', 'Contributor', 'Editor']))

        return create(Builder('inbox')
                      .titled(u'Inbox')
                      .within(container)
                      .having(responsible_org_unit='fa'))

    def create_private_folder(self):
        private_root = create(Builder('private_root'))
        mtool = api.portal.get_tool('portal_membership')
        mtool.setMembersFolderById(private_root.id)
        mtool.setMemberAreaType('opengever.private.folder')
        mtool.setMemberareaCreationFlag()
        mtool.createMemberArea(member_id=self.regular_user.getId())
        return private_root[self.regular_user.getId()]

    def prepare_request(self, userid='', destination='inbox', org_unit=''):
        fields = {
            'userid': userid or self.regular_user.getId(),
            'destination': destination,
            'file': ('mydocument.txt', 'my text', 'text/plain'),
        }
        if org_unit:
            fields['org_unit'] = org_unit

        encoder = MultipartEncoder(fields=fields)
        return encoder.to_string(), {
            'Content-Type': encoder.content_type,
            'Accept': 'application/json',
        }

    @browsing
    def test_scanin_to_inbox(self, browser):
        self.login(self.regular_user, browser)
        self.create_single_inbox()
        body, headers = self.prepare_request()

        browser.open(self.portal.absolute_url() + '/@scan-in',
                     method='POST',
                     headers=headers,
                     data=body)

        self.assertEqual(201, browser.status_code)
        self.login(self.administrator, browser)

        doc = self.inbox.objectValues()[-1]
        self.assertEqual('mydocument', doc.Title())

    @browsing
    def test_scanin_to_inbox_without_permission(self, browser):
        self.login(self.administrator, browser)
        body, headers = self.prepare_request(
            userid=self.dossier_responsible.getId())
        browser.exception_bubbling = True
        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(self.portal.absolute_url() + '/@scan-in',
                         method='POST',
                         headers=headers,
                         data=body)

        expected_message = 'The user does not have the required permissions to perform a scan-in via the API.'
        self.assertEqual(expected_message, browser.json.get('error').get('message'))

    @browsing
    def test_scanin_to_org_unit_inbox(self, browser):
        self.login(self.regular_user, browser)
        inbox = self.create_org_unit_inbox()

        body, headers = self.prepare_request(org_unit='fa')
        browser.open(self.portal.absolute_url() + '/@scan-in',
                     method='POST',
                     headers=headers,
                     data=body)

        self.assertEqual(201, browser.status_code)
        doc = inbox.objectValues()[0]
        self.assertEqual('mydocument', doc.Title())

    @browsing
    def test_scanin_to_org_unit_inbox_by_title(self, browser):
        self.login(self.regular_user, browser)
        inbox = self.create_org_unit_inbox()

        body, headers = self.prepare_request(org_unit=u'Finanz\xe4mt')
        browser.open(self.portal.absolute_url() + '/@scan-in',
                     method='POST',
                     headers=headers,
                     data=body)

        self.assertEqual(201, browser.status_code)
        doc = inbox.objectValues()[0]
        self.assertEqual('mydocument', doc.Title())

    @browsing
    def test_scanin_to_new_private_dossier(self, browser):
        self.login(self.manager, browser)
        private_folder = self.create_private_folder()

        body, headers = self.prepare_request(destination='private')
        browser.open(self.portal.absolute_url() + '/@scan-in',
                     method='POST',
                     headers=headers,
                     data=body)

        self.assertEqual(201, browser.status_code)
        dossier = private_folder.objectValues()[0]
        self.assertEqual('Scaneingang', dossier.Title())
        self.assertIsNotNone(IUUID(dossier))
        self.assertIsNotNone(obj2brain(dossier).UID)
        doc = dossier.objectValues()[0]
        self.assertEqual('mydocument', doc.Title())

    @browsing
    def test_scanin_to_existing_private_dossier(self, browser):
        self.login(self.manager, browser)
        private_folder = self.create_private_folder()
        dossier = create(Builder('private_dossier')
                         .within(private_folder)
                         .titled(u'Scaneingang'))

        body, headers = self.prepare_request(destination='private')
        browser.open(self.portal.absolute_url() + '/@scan-in',
                     method='POST',
                     headers=headers,
                     data=body)

        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(private_folder.objectIds()))
        doc = dossier.objectValues()[0]
        self.assertEqual('mydocument', doc.Title())

    @browsing
    def test_scanin_to_missing_private_dossier(self, browser):
        self.login(self.manager, browser)

        body, headers = self.prepare_request(destination='private')
        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(self.portal.absolute_url() + '/@scan-in',
                         method='POST',
                         headers=headers,
                         data=body)

        expected_message = 'The scan-in destination does not exist.'
        self.assertIn(expected_message, browser.json.get('error').get('message'))

    @browsing
    def test_scanin_with_missing_userid(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal.absolute_url() + '/@scan-in',
                         method='POST',
                         headers={'Accept': 'application/json'},
                         data={})
        self.assertIn('Missing userid.', browser.contents)

    @browsing
    def test_scanin_with_unkown_userid(self, browser):
        self.login(self.regular_user, browser)

        body, headers = self.prepare_request(userid='chief')
        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(self.portal.absolute_url() + '/@scan-in',
                         method='POST',
                         headers=headers,
                         data=body)
        self.assertIn('Unknown user.', browser.contents)

    @browsing
    def test_scanin_without_file(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.portal.absolute_url() + '/@scan-in',
                         method='POST',
                         headers={'Accept': 'application/json'},
                         data={'userid': self.regular_user.getId()})
        self.assertIn('Missing file.', browser.contents)

    @browsing
    def test_scanin_to_unknown_destination(self, browser):
        self.login(self.regular_user, browser)

        body, headers = self.prepare_request(destination='unknown')
        with browser.expect_http_error(code=404, reason='Not Found'):
            browser.open(self.portal.absolute_url() + '/@scan-in',
                         method='POST',
                         headers=headers,
                         data=body)

        expected_message = 'The scan-in destination does not exist.'
        self.assertIn(expected_message, browser.json.get('error').get('message'))
