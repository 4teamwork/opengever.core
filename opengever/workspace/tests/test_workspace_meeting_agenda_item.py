from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
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

    @browsing
    def test_can_add_todo_list_reference(self, browser):
        self.login(self.workspace_member, browser)
        headers = self.api_headers.copy()
        headers.update({'Prefer': 'return=representation'})

        browser.open(self.workspace_meeting_agenda_item, method='PATCH',
                     headers=headers,
                     data=json.dumps({'related_todo_list': self.todolist_general.UID()}))

        self.assertEqual(
            self.todolist_general.absolute_url(),
            browser.json.get('related_todo_list')['@id']
        )

    @browsing
    def test_only_todo_lists_from_the_current_workspace_are_allowed_to_reference(self, browser):
        self.login(self.workspace_member, browser)
        headers = self.api_headers.copy()
        headers.update({'Prefer': 'return=representation'})

        workspace2 = create(Builder('workspace').within(self.workspace_root))
        todolist = create(Builder('todolist')
                          .titled(u'Foreign workspace')
                          .within(workspace2))

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(self.workspace_meeting_agenda_item, method='PATCH',
                         headers=headers,
                         data=json.dumps({'related_todo_list': todolist.UID()}))

        self.assertEqual("[{'field': 'related_todo_list', 'message': u'Constraint not satisfied', 'error': 'ValidationError'}]",
                         str(cm.exception))

    @browsing
    def test_members_can_delete_workspace_meeting_agenda_item(self, browser):
        self.login(self.workspace_member, browser)
        workspace_meeting_agenda_item_id = self.workspace_meeting_agenda_item.id
        self.assertIn(workspace_meeting_agenda_item_id, self.workspace_meeting.objectIds())
        browser.open(self.workspace_meeting_agenda_item, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(workspace_meeting_agenda_item_id, self.workspace_meeting.objectIds())

    @browsing
    def test_admins_can_delete_workspace_meeting_agenda_item(self, browser):
        self.login(self.workspace_admin, browser)
        workspace_meeting_agenda_item_id = self.workspace_meeting_agenda_item.id
        self.assertIn(workspace_meeting_agenda_item_id, self.workspace_meeting.objectIds())
        browser.open(self.workspace_meeting_agenda_item, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(workspace_meeting_agenda_item_id, self.workspace_meeting.objectIds())

    @browsing
    def test_managers_can_delete_workspace_meeting_agenda_item(self, browser):
        self.login(self.manager, browser)
        workspace_meeting_agenda_item_id = self.workspace_meeting_agenda_item.id
        self.assertIn(workspace_meeting_agenda_item_id, self.workspace_meeting.objectIds())
        browser.open(self.workspace_meeting_agenda_item, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(workspace_meeting_agenda_item_id, self.workspace_meeting.objectIds())

    @browsing
    def test_guests_cannot_delete_workspace_meeting_agenda_item(self, browser):
        self.login(self.workspace_guest, browser)
        workspace_meeting_agenda_item_id = self.workspace_meeting_agenda_item.id
        with browser.expect_http_error(403):
            browser.open(self.workspace_meeting_agenda_item, method='DELETE', headers=self.api_headers)

        self.assertIn(workspace_meeting_agenda_item_id, self.workspace_meeting.objectIds())


class TestWorkspaceMeetingAgendaItemSolr(SolrIntegrationTestCase):

    @browsing
    def test_members_can_change_order(self, browser):
        self.login(self.workspace_member, browser)

        create(Builder('workspace meeting agenda item')
               .within(self.workspace_meeting)
               .titled(u'Intro'))

        self.commit_solr()
        browser.open(self.workspace_meeting,
                     view='@solrsearch?sort=getObjPositionInParent asc&depth=1'
                          '&fl=id&fq=portal_type:opengever.workspace.meetingagendaitem',
                     headers=self.api_headers)

        self.assertEqual(['agendaitem-1', 'agendaitem-2'],
                         [item.get('id') for item in browser.json.get('items')])

        data = {
            'ordering': {
                'obj_id': 'agendaitem-1',
                'delta': '1',
                'subset_ids': ['agendaitem-1', 'agendaitem-2']}}

        browser.open(self.workspace_meeting, method='PATCH',
                     headers=self.api_headers, data=json.dumps(data))
        self.commit_solr()
        self.assertEqual(204, browser.status_code)
        browser.open(self.workspace_meeting,
                     view='@solrsearch?sort=getObjPositionInParent asc&depth=1'
                          '&fl=id&fq=portal_type:opengever.workspace.meetingagendaitem',
                     headers=self.api_headers)

        self.assertEqual(['agendaitem-2', 'agendaitem-1'],
                         [item.get('id') for item in browser.json.get('items')])

    @browsing
    def test_guests_cannot_change_order(self, browser):
        self.login(self.workspace_guest, browser)

        create(Builder('workspace meeting agenda item')
               .within(self.workspace_meeting)
               .titled(u'Intro'))

        data = {
            'ordering': {
                'obj_id': 'agendaitem-1',
                'delta': '1',
                'subset_ids': ['agendaitem-1', 'agendaitem-2']}}

        with browser.expect_http_error(401):
            browser.open(self.workspace_meeting, method='PATCH',
                         headers=self.api_headers, data=json.dumps(data))

    @browsing
    def test_workspace_agendaitems_are_indexed_in_meeting_searchable_text(self, browser):
        self.login(self.workspace_member, browser)
        # builder of workspace_meeting_agendaitem does not reindex
        # the workspace meeting
        self.workspace_meeting.reindexObject()
        self.commit_solr()

        searchable_text = solr_data_for(self.workspace_meeting, 'SearchableText')

        self.assertEqual(
            u'Genehmigung des Lageberichts',
            self.workspace_meeting_agenda_item.title)
        self.assertIn(
            u'Genehmigung des Lageberichts',
            searchable_text)

        self.assertEqual(
            u'Der Lagebericht 2018 steht zur Verf\xfcgung und muss genehmigt werden',
            self.workspace_meeting_agenda_item.text.raw)
        self.assertIn(
            u'Der Lagebericht 2018 steht zur Verf\xfcgung und muss genehmigt werden',
            searchable_text)

        self.assertEqual(
            u'Die <a href="http://example.com">Gener\xe4lversammlung</a> '
            'genehmigt den <b>Lagebericht</b> 2018',
            self.workspace_meeting_agenda_item.decision.raw)
        self.assertIn(
            u'Die  Gener\xe4lversammlung  genehmigt den Lagebericht 2018',
            searchable_text)

    @browsing
    def test_workspace_meeting_gets_reindexed_when_agendaitem_is_modified(self, browser):
        self.login(self.workspace_member, browser)
        # builder of workspace_meeting_agendaitem does not reindex
        # the workspace meeting
        self.workspace_meeting.reindexObject()
        self.commit_solr()

        searchable_text = solr_data_for(self.workspace_meeting, 'SearchableText')
        self.assertNotIn("Danger text", searchable_text)
        self.assertNotIn("Danger decision", searchable_text)

        headers = self.api_headers.copy()
        headers.update({'Prefer': 'return=representation'})
        browser.open(self.workspace_meeting_agenda_item, method='PATCH',
                     headers=headers,
                     data=json.dumps({
                         'text': u'Danger<script>alert("foo")</script> text',
                         'decision': u'Danger<script>alert("foo")</script> decision'}))

        self.commit_solr()
        searchable_text = solr_data_for(self.workspace_meeting, 'SearchableText')
        self.assertIn("Danger text", searchable_text)
        self.assertIn("Danger decision", searchable_text)

    @browsing
    def test_workspace_meeting_gets_reindexed_when_agendaitem_is_added(self, browser):
        self.login(self.workspace_member, browser)
        # builder of workspace_meeting_agendaitem does not reindex
        # the workspace meeting
        self.workspace_meeting.reindexObject()
        self.commit_solr()

        searchable_text = solr_data_for(self.workspace_meeting, 'SearchableText')
        self.assertNotIn(u'\xc4 new title', searchable_text)
        self.assertNotIn(u'My <b>bold</b> text', searchable_text)
        self.assertNotIn(u'My <b>bold</b> decision', searchable_text)

        data = {
            '@type': u'opengever.workspace.meetingagendaitem',
            'title': u'\xc4 new title',
            'text': u'My <b>bold</b> text',
            'decision': None,
        }
        browser.open(self.workspace_meeting,
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps(data))

        self.commit_solr()
        searchable_text = solr_data_for(self.workspace_meeting, 'SearchableText')
        self.assertIn(u'\xc4 new title', searchable_text)
        self.assertIn(u'My bold text', searchable_text)
        self.assertNotIn(u'None', searchable_text)

    @browsing
    def test_workspace_meeting_agendaitems_are_excluded_from_search(self, browser):
        self.login(self.workspace_member, browser)
        url = u'{}/@solrsearch?fq=UID:{}'.format(
            self.portal.absolute_url(), self.workspace_meeting_agenda_item.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(0, browser.json["items_total"])
