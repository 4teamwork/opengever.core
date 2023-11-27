from DateTime import DateTime
from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.behaviors.touched import ITouched
from opengever.journal.manager import JournalManager
from opengever.testing import IntegrationTestCase
import json
import pytz


def http_headers():
    return {'Accept': 'application/json',
            'Content-Type': 'application/json'}


class TestJournalPost(IntegrationTestCase):

    def journal_entries(self, obj):
        return JournalManager(obj).list()

    @browsing
    def test_add_journal_entry(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            'comment': 'example comment',
            'category': {'token': 'information'},
            'related_documents': [self.document.absolute_url()],
            'time': '2016-12-09T09:40:00'}

        browser.open(
            self.dossier.absolute_url() + '/@journal',
            data=json.dumps(payload),
            method='POST',
            headers=http_headers(),
        )

        entry = self.journal_entries(self.dossier)[-1]
        self.assertEqual('example comment', entry['comments'])
        self.assertEqual(self.regular_user.id, entry['actor'])
        self.assertEqual(DateTime('2016-12-09T09:40:00'), entry['time'])

        documents = entry.get('action').get('documents')
        self.assertEqual(1, len(documents))
        self.assertEqual(self.document.title, documents[0].get('title'))

    @browsing
    def test_post_raises_when_category_does_not_exist(self, browser):
        self.login(self.regular_user, browser)
        payload = {'comment': 'Foo', 'category': 'not-existing'}

        with browser.expect_http_error(500):
            browser.open(
                self.dossier.absolute_url() + '/@journal',
                data=json.dumps(payload),
                method='POST',
                headers=http_headers(),
            )

    @browsing
    def test_post_raises_when_document_lookup_failed(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            'comment': 'Foo',
            'related_documents': [
                'https://not-existing',
                self.portal.absolute_url() + '/not-existing',
                self.dossier.absolute_url(),
                self.document.absolute_url()]}

        with browser.expect_http_error(500):
            browser.open(
                self.dossier.absolute_url() + '/@journal',
                data=json.dumps(payload),
                method='POST',
                headers=http_headers(),
            )

    @browsing
    def test_add_journal_entry_via_api_is_xss_safe(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='@journal', method='POST',
                     headers=self.api_headers,
                     data=json.dumps({
                         'comment': u'<p>Danger<script>alert("foo")</script> text</p>',
                         'category': u'information'}))

        entry = self.journal_entries(self.dossier)[-1]
        self.assertEqual('<p>Danger text</p>', entry['comments'])

    @browsing
    def test_add_journal_entry_updates_touched_date(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            'comment': 'example comment',
            'category': {'token': 'information'},
        }

        self.assertEqual("2016-08-31", str(ITouched(self.dossier).touched))
        with freeze(datetime(2020, 6, 13)):
            browser.open(
                self.dossier.absolute_url() + '/@journal',
                data=json.dumps(payload),
                method='POST',
                headers=http_headers(),
            )

        self.assertEqual("2020-06-13", str(ITouched(self.dossier).touched))


class TestJournalGet(IntegrationTestCase):

    def clear_journal_entries(self, obj):
        JournalManager(obj).clear()

    @browsing
    def test_returns_empty_list_if_no_jounral_entries_are_available(self, browser):
        self.login(self.regular_user, browser)
        self.clear_journal_entries(self.dossier)

        response = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertEqual([], response.get('items'))

    @browsing
    def test_returns_journal_entries_sorted_by_time_with_newest_first(self, browser):
        self.login(self.regular_user, browser)
        self.clear_journal_entries(self.dossier)

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            JournalManager(self.dossier).add_manual_entry('information', 'first')
        JournalManager(self.dossier).add_manual_entry(
            'information', 'second', time=DateTime(u'2016-12-01T12:34:00+00:00'))
        JournalManager(self.dossier).add_manual_entry(
            'information', 'third', time=DateTime(u'2017-10-16T11:34:00+00:00'))

        response = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json

        entry_titles = [item.get('comment') for item in response.get('items')]
        self.assertEqual(['third', 'first', 'second'], entry_titles)

    @browsing
    def test_entries_with_identical_timestamp_are_sorted_by_newset_first(self, browser):
        self.login(self.regular_user, browser)
        self.clear_journal_entries(self.dossier)

        JournalManager(self.dossier).add_manual_entry(
            'information', 'first', time=DateTime(u'2016-12-01T12:34:00+00:00'))
        JournalManager(self.dossier).add_manual_entry(
            'information', 'second', time=DateTime(u'2016-12-01T12:34:00+00:00'))
        JournalManager(self.dossier).add_manual_entry(
            'information', 'third', time=DateTime(u'2016-12-01T12:34:00+00:00'))

        response = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json

        entry_titles = [item.get('comment') for item in response.get('items')]
        self.assertEqual(['third', 'second', 'first'], entry_titles)

    @browsing
    def test_show_total_items(self, browser):
        self.login(self.regular_user, browser)
        self.clear_journal_entries(self.dossier)

        JournalManager(self.dossier).add_manual_entry('information', 'first')
        JournalManager(self.dossier).add_manual_entry('information', 'second')

        browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        )

        response = browser.json

        self.assertEqual(2, response.get('items_total'))

    @browsing
    def test_listing_is_batched(self, browser):
        self.login(self.regular_user, browser)
        self.clear_journal_entries(self.dossier)

        JournalManager(self.dossier).add_manual_entry('information', 'first')
        JournalManager(self.dossier).add_manual_entry('information', 'second')
        JournalManager(self.dossier).add_manual_entry('information', 'third')

        response = browser.open(
            self.dossier.absolute_url() + '/@journal?b_size=2',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertEqual(3, response.get('items_total'))
        self.assertEqual(2, len(response.get('items')))
        self.assertIn('batching', response)

    @browsing
    def test_validate_item_fields(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            manager.add_manual_entry(
                'information', 'is an agent',
                documents=[self.document])
            manager.list()[-1]['id'] = '123-456-789'  # mock id

        response = browser.open(
            self.dossier.absolute_url() + '/@journal?b_size=2',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertDictEqual({
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/@journal/123-456-789',
            u'id': '123-456-789',
            u'is_editable': True,
            u'actor_fullname': u'B\xe4rfuss K\xe4thi',
            u'actor_id': u'kathi.barfuss',
            u'comment': u'is an agent',
            u'category': {'token': 'information', 'title': 'Information' },
            u'related_documents': [{
                u'@id': self.document.absolute_url(),
                u'@type': u'opengever.document.document',
                u'UID': u'createtreatydossiers000000000002',
                u'checked_out': None,
                u'description': self.document.description,
                u'file_extension': u'.docx',
                u'is_leafnode': None,
                u'review_state': u'document-state-draft',
                u'title': self.document.title}],
            u'time': u'2017-10-16T00:00:00+00:00',
            u'title': u'Information'
        }, response.get('items')[0])

    @browsing
    def test_can_filter_by_manual_entries_only(self, browser):
        self.login(self.regular_user, browser)

        JournalManager(self.dossier).add_manual_entry('information', 'Manual entry 1')
        JournalManager(self.dossier).add_manual_entry('information', 'Manual entry 2')

        response = browser.open(
            self.dossier, view='@journal', method='GET', headers=http_headers())

        self.assertEqual(19, response.json.get('items_total'))

        response = browser.open(
            self.dossier, view='@journal?filters.manual_entries_only:record:boolean=True',
            method='GET', headers=http_headers())

        self.assertEqual(
            ['Manual entry 2', 'Manual entry 1'],
            map(lambda item: item.get('comment'), response.json.get('items')))

    @browsing
    def test_can_filter_by_categories(self, browser):
        self.login(self.regular_user, browser)

        JournalManager(self.dossier).add_manual_entry('information', 'my information')
        JournalManager(self.dossier).add_manual_entry('phone-call', 'my phone call')

        response = browser.open(
            self.dossier, view='@journal', method='GET', headers=http_headers())

        self.assertEqual(19, response.json.get('items_total'))

        response = browser.open(
            self.dossier, view='@journal?filters.categories:record:list=phone-call',
            method='GET', headers=http_headers())

        self.assertEqual(
            ['my phone call'],
            map(lambda item: item.get('comment'), response.json.get('items')))

    @browsing
    def test_can_search_by_comment(self, browser):
        self.login(self.regular_user, browser)

        JournalManager(self.dossier).add_manual_entry('information', 'my information')
        JournalManager(self.dossier).add_manual_entry('phone-call', u'my phone c\xe4ll')

        response = browser.open(
            self.dossier, view='@journal', method='GET', headers=http_headers())

        self.assertEqual(19, response.json.get('items_total'))

        response = browser.open(
            self.dossier, view='@journal?search=c\xc3\xa4ll',
            method='GET', headers=http_headers())

        self.assertEqual(
            [u'my phone c\xe4ll'],
            map(lambda item: item.get('comment'), response.json.get('items')))

    @browsing
    def test_can_search_by_title(self, browser):
        self.login(self.regular_user, browser)

        JournalManager(self.dossier).add_manual_entry('information', 'my information')
        JournalManager(self.dossier).add_manual_entry('phone-call', u'my phone c\xe4ll')

        response = browser.open(
            self.dossier, view='@journal', method='GET', headers=http_headers())

        self.assertEqual(19, response.json.get('items_total'))

        response = browser.open(
            self.dossier, view='@journal?search=call',
            method='GET', headers=http_headers())

        self.assertEqual(
            [u'Phone call'],
            map(lambda item: item.get('title'), response.json.get('items')))

    @browsing
    def test_manual_entries_are_flagged_as_editable(self, browser):
        self.login(self.regular_user, browser)

        JournalManager(self.dossier).add_manual_entry('information', 'Manual entry')

        response = browser.open(
            self.dossier, view='@journal', method='GET', headers=http_headers())

        self.assertTrue(response.json.get('items')[0].get('is_editable'))

    @browsing
    def test_old_manual_entries_without_id_are_flagged_as_non_editable(self, browser):
        self.login(self.regular_user, browser)

        JournalManager(self.dossier).add_manual_entry('information', 'Manual entry without id (old entry)')

        manager = JournalManager(self.dossier)
        manager.list()[-1]['id'] = None  # remove id

        response = browser.open(
            self.dossier, view='@journal', method='GET', headers=http_headers())

        self.assertFalse(response.json.get('items')[0].get('is_editable'))

    @browsing
    def test_auto_journal_entries_are_flagged_as_non_editable(self, browser):
        self.login(self.regular_user, browser)

        response = browser.open(
            self.dossier, view='@journal', method='GET', headers=http_headers())

        self.assertFalse(response.json.get('items')[0].get('is_editable'))


class TestJournalDelete(IntegrationTestCase):

    @browsing
    def test_removes_entry_with_the_provided_id(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        manager.add_manual_entry('information', 'first')
        manager.add_manual_entry('information', 'second')

        first_entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        self.assertEqual(2, manager.count())
        browser.open(first_entry.get('@id'), method='DELETE', headers=http_headers())

        self.assertEqual(204, browser.status_code)
        self.assertEqual(1, manager.count())
        entry_titles = [item.get('comments') for item in manager.list()]
        self.assertEqual(['second'], entry_titles)

    @browsing
    def test_raises_when_id_does_not_exist(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(404):
            url = '{}/@journal/{}'.format(self.dossier.absolute_url(), 'invalid')
            browser.open(url, method='DELETE',
                         headers={'Accept': 'application/json'})

    @browsing
    def test_raises_without_edit_permission(self, browser):
        self.login(self.regular_user, browser=browser)

        manager = JournalManager(self.inactive_dossier)
        manager.clear()

        manager.add_manual_entry('information', 'first')
        self.assertEqual(1, manager.count())

        entry = browser.open(
            self.inactive_dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        with browser.expect_http_error(401):
            browser.open(entry.get('@id'), method='DELETE',
                         headers={'Accept': 'application/json'})

        self.assertEqual(1, manager.count())

    @browsing
    def test_raises_when_deleting_a_non_manual_journal_entry(self, browser):
        self.login(self.regular_user, browser=browser)

        entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        with browser.expect_http_error(403):
            browser.open(entry.get('@id'), method='DELETE',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'message': u'Only manual journal entries can be removed',
             u'type': u'Forbidden'}, browser.json)

    @browsing
    def test_delete_journal_entry_updates_touched_date(self, browser):
        self.login(self.regular_user, browser)
        manager = JournalManager(self.dossier)
        manager.clear()

        manager.add_manual_entry('information', 'first')

        self.assertEqual("2016-08-31", str(ITouched(self.dossier).touched))
        first_entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        with freeze(datetime(2020, 6, 13)):
            browser.open(first_entry.get('@id'), method='DELETE', headers=http_headers())

        self.assertEqual("2020-06-13", str(ITouched(self.dossier).touched))


class TestJournalPatch(IntegrationTestCase):

    @browsing
    def test_can_patch_an_existing_journal_entry(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        manager.add_manual_entry('information', 'is an agent')

        self.assertEqual(1, manager.count())
        entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        browser.open(entry.get('@id'),
                     method='PATCH',
                     data=json.dumps({
                         "comment": "my new comment",
                         "category": "phone-call",
                         'related_documents': [self.document.absolute_url()],
                         'time': u'2017-10-16T00:00:00+00:00',
                     }),
                     headers=http_headers())
        self.assertEqual(1, manager.count())

        entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        self.assertEqual(u'my new comment', entry.get('comment'))
        self.assertEqual(u'Phone call', entry.get('title'))
        self.assertEqual(u'2017-10-16T00:00:00+00:00', entry['time'])
        self.assertEqual(
            self.document.absolute_url(),
            entry.get('related_documents')[0].get('@id'))

    @browsing
    def test_raises_when_id_does_not_exist(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(404):
            url = '{}/@journal/{}'.format(self.dossier.absolute_url(), 'invalid')
            browser.open(url, method='PATCH',
                         headers={'Accept': 'application/json'})

    @browsing
    def test_raises_when_updating_a_non_manual_journal_entry(self, browser):
        self.login(self.regular_user, browser=browser)

        entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        with browser.expect_http_error(403):
            browser.open(entry.get('@id'), method='PATCH',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'message': u'Only manual journal entries can be updated',
             u'type': u'Forbidden'}, browser.json)

    @browsing
    def test_raises_without_edit_permission(self, browser):
        self.login(self.regular_user, browser=browser)

        manager = JournalManager(self.inactive_dossier)
        manager.clear()

        manager.add_manual_entry('information', 'first')
        self.assertEqual(1, manager.count())

        entry = browser.open(
            self.inactive_dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        with browser.expect_http_error(401):
            browser.open(entry.get('@id'),
                         method='PATCH',
                         data=json.dumps({}),
                         headers=http_headers())

        self.assertEqual(1, manager.count())

    @browsing
    def test_raises_when_category_does_not_exist(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        manager.add_manual_entry('information', 'is an agent')

        entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        with browser.expect_http_error(400):
            browser.open(entry.get('@id'),
                         method='PATCH',
                         data=json.dumps({
                             "category": "invalid",
                         }),
                         headers=http_headers())

        self.assertEqual(
            {u'message': u'ConstraintNotSatisfied: invalid',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_raises_when_document_lookup_failed(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        manager.add_manual_entry('information', 'is an agent')

        entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        with browser.expect_http_error(400):
            browser.open(entry.get('@id'),
                         method='PATCH',
                         data=json.dumps({
                             'related_documents': ['https://not-existing']
                         }),
                         headers=http_headers())

        self.assertEqual(
            {u'message': u'ValueError: Could not resolve object for UID=https://not-existing',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_patch_journal_entry_via_api_is_xss_safe(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        manager.add_manual_entry('information', 'is an agent')

        entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        browser.open(entry.get('@id'),
                     method='PATCH',
                     data=json.dumps({
                         'comment': u'<p>Danger<script>alert("foo")</script> text</p>',
                     }),
                     headers=http_headers())

        entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        self.assertEqual('<p>Danger text</p>', entry['comment'])

    @browsing
    def test_patch_journal_entry_updates_touched_date(self, browser):
        self.login(self.regular_user, browser)

        manager = JournalManager(self.dossier)
        manager.clear()

        manager.add_manual_entry('information', 'is an agent')

        entry = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json.get('items')[-1]

        self.assertEqual("2016-08-31", str(ITouched(self.dossier).touched))
        with freeze(datetime(2020, 6, 13)):
            browser.open(entry.get('@id'),
                         method='PATCH',
                         data=json.dumps({
                             "comment": "my new comment",
                             "category": "phone-call",
                             'related_documents': [self.document.absolute_url()],
                             'time': u'2017-10-16T00:00:00+00:00',
                         }),
                         headers=http_headers())

        self.assertEqual("2020-06-13", str(ITouched(self.dossier).touched))
