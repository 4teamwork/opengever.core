from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestSaveMinutesAsPDFPost(IntegrationTestCase):

    @browsing
    def test_save_minutes_as_pdf_post_not_available_for_guests(self, browser):
        self.login(self.workspace_guest, browser=browser)

        with browser.expect_http_error(401):
            browser.open(self.workspace, view='@save-minutes-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"meeting_uid": self.workspace_meeting.UID()}))

        with browser.expect_http_error(401):
            browser.open(self.workspace_folder, view='@save-minutes-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"meeting_uid": self.workspace_meeting.UID()}))

    @browsing
    def test_save_minutes_as_pdf_post(self, browser):
        self.login(self.workspace_member, browser=browser)

        with self.observe_children(self.workspace_folder) as children:
            browser.open(self.workspace_folder, view='@save-minutes-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"meeting_uid": self.workspace_meeting.UID()}))

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()
        self.assertEqual(browser.status_code, 201)
        self.assertEqual(created_document.absolute_url(),
                         browser.headers['location'])

        self.assertEqual('Minutes for Besprechung Kl\xc3\xa4ranlage',
                         created_document.Title())
        self.assertEqual(created_document.Creator(), self.workspace_member.getId())
        self.assertEqual(u'Minutes for Besprechung Klaeranlage.pdf',
                         created_document.get_filename())

    @browsing
    def test_save_minutes_as_pdf_post_without_meeting_uid_raises_bad_request(self, browser):
        self.login(self.workspace_member, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.workspace, view='@save-minutes-as-pdf', method='POST',
                         headers=self.api_headers)

        self.assertEqual({
            "message": "Property 'meeting_uid' is required and should be a UID of a WorkspaceMeeting",
            "type": "BadRequest"}, browser.json)

    @browsing
    def test_save_minutes_as_pdf_post_with_invalid_meeting_uid_raises_bad_request(self, browser):
        self.login(self.workspace_member, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.workspace_folder, view='@save-minutes-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"meeting_uid": self.task.UID()}))

        self.assertEqual({
            "message": "Property 'meeting_uid' is required and should be a UID of a WorkspaceMeeting",
            "type": "BadRequest"}, browser.json)

    @browsing
    def test_save_minutes_as_pdf_post_is_available_for_workspaces(self, browser):
        self.login(self.workspace_member, browser)
        with self.observe_children(self.workspace) as children:
            browser.open(self.workspace, view='@save-minutes-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"meeting_uid": self.workspace_meeting.UID()}))

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()
        self.assertEqual(browser.status_code, 201)
        self.assertEqual(created_document.absolute_url(), browser.headers['location'])

    @browsing
    def test_save_minutes_as_pdf_post_is_available_for_workspace_folders(self, browser):
        self.login(self.workspace_member, browser)
        with self.observe_children(self.workspace_folder) as children:
            browser.open(self.workspace_folder, view='@save-minutes-as-pdf', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"meeting_uid": self.workspace_meeting.UID()}))

        self.assertEqual(len(children["added"]), 1)
        created_document = children["added"].pop()
        self.assertEqual(browser.status_code, 201)
        self.assertEqual(created_document.absolute_url(), browser.headers['location'])
