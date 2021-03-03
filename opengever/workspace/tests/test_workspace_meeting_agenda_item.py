from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zExceptions import BadRequest
import json


class TestWorkspaceMeetingAgendaItem(IntegrationTestCase):

    @browsing
    def test_get_workspace_meeting_agenda_item(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting_agenda_item, method='GET', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        expected = {
            u'@id': self.workspace_meeting_agenda_item.absolute_url(),
            u'@type': u'opengever.workspace.meetingagendaitem',
            u'id': u'agendaitem-1',
            u'title': u'Genehmigung des Lageberichts',
            u'review_state': None,
        }
        self.assertDictContainsSubset(expected, browser.json)
        self.assertEqual(
            u'Der Lagebericht 2018 steht zur Verf\xfcgung und muss genehmigt werden',
            browser.json.get('text').get('data'))
        self.assertEqual(
            u'Die <a href="http://example.com">Gener\xe4lversammlung</a> genehmigt den <b>Lagebericht</b> 2018',
            browser.json.get('decision').get('data'))
        self.assertEqual(
            [self.workspace_document.absolute_url()],
            [item['@id'] for item in browser.json.get('relatedItems')])

    @browsing
    def test_post_workspace_meeting_agenda_item(self, browser):
        self.login(self.workspace_member, browser)
        data = {
            '@type': u'opengever.workspace.meetingagendaitem',
            'title': u'\xc4 new title',
            'text': u'My <b>bold</b> text',
            'decision': u'My <b>bold</b> decision',
            'relatedItems': [self.workspace_document.UID()],
        }
        browser.open(self.workspace_meeting, method='POST', headers=self.api_headers, data=json.dumps(data))

        self.assertEqual(201, browser.status_code)
        self.assertEqual(u'\xc4 new title', browser.json.get('title'))
        self.assertEqual(u'My <b>bold</b> text', browser.json.get('text').get('data'))
        self.assertEqual(u'My <b>bold</b> decision', browser.json.get('decision').get('data'))
        self.assertEqual(
            [self.workspace_document.absolute_url()],
            [item['@id'] for item in browser.json.get('relatedItems')])

    @browsing
    def test_update_workspace_meeting_agenda_item(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_meeting_agenda_item, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'title': u'\xc4 new title'}))

        self.assertEqual(204, browser.status_code)
        self.assertEqual(u'\xc4 new title', self.workspace_meeting_agenda_item.title)

    @browsing
    def test_richt_text_fields_are_safe_html(self, browser):
        self.login(self.workspace_member, browser)
        headers = self.api_headers.copy()
        headers.update({'Prefer': 'return=representation'})
        browser.open(self.workspace_meeting_agenda_item, method='PATCH',
                     headers=headers,
                     data=json.dumps({
                         'text': u'Danger<script>alert("foo")</script> text',
                         'decision': u'Danger<script>alert("foo")</script> decision'}))

        self.assertEqual(u'Danger text', browser.json.get('text').get('data'))
        self.assertEqual(u'Danger decision', browser.json.get('decision').get('data'))

    @browsing
    def test_only_documents_from_the_current_workspace_are_allowed_to_reference(self, browser):
        self.login(self.workspace_member, browser)
        headers = self.api_headers.copy()
        headers.update({'Prefer': 'return=representation'})

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(self.workspace_meeting_agenda_item, method='PATCH',
                         headers=headers,
                         data=json.dumps({'relatedItems': [self.document.UID()]}))

        self.assertEqual("[{'field': 'relatedItems', 'message': u'Constraint not satisfied', 'error': 'ValidationError'}]",
                         str(cm.exception))
