from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.journal.manager import JournalManager
from opengever.testing import IntegrationTestCase
from zope.annotation import IAnnotations
import json
import pytz


def http_headers():
    return {'Accept': 'application/json',
            'Content-Type': 'application/json'}


class TestJournalPost(IntegrationTestCase):

    def journal_entries(self, obj):
        return IAnnotations(obj).get(JOURNAL_ENTRIES_ANNOTATIONS_KEY)

    @browsing
    def test_add_journal_entry(self, browser):
        self.login(self.regular_user, browser)
        payload = {'comment': 'example comment', 'category': 'information',
                   'related_documents': [self.document.absolute_url()]}

        browser.open(
            self.dossier.absolute_url() + '/@journal',
            data=json.dumps(payload),
            method='POST',
            headers=http_headers(),
        )

        entry = self.journal_entries(self.dossier)[-1]
        self.assertEqual('example comment', entry['comments'])
        self.assertEqual(self.regular_user.id, entry['actor'])

        documents = entry.get('action').get('documents')
        self.assertEqual(1, len(documents))
        self.assertEqual(self.document.title, documents[0].get('title'))

    @browsing
    def test_post_raises_when_comment_is_missing(self, browser):
        self.login(self.regular_user, browser)
        payload = {'category': 'information'}

        with browser.expect_http_error(400):
            browser.open(
                self.dossier.absolute_url() + '/@journal',
                data=json.dumps(payload),
                method='POST',
                headers=http_headers(),
            )

        self.assertEqual(
            {"message": "The request body requires the 'comment' attribute",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_post_raises_when_category_does_not_exist(self, browser):
        self.login(self.regular_user, browser)
        payload = {'comment': 'Foo', 'category': 'not-existing'}

        with browser.expect_http_error(400):
            browser.open(
                self.dossier.absolute_url() + '/@journal',
                data=json.dumps(payload),
                method='POST',
                headers=http_headers(),
            )

        self.assertEqual(
            {"message": "The provided 'category' does not exists.",
             "type": "BadRequest"},
            browser.json)

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

        self.assertEqual(
            {u'message': u'Could not resolve object for UID=https://not-existing',
             u'type': u'ValueError'},
            browser.json)

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


class TestJournalGet(IntegrationTestCase):

    def clear_journal_entries(self, obj):
        del IAnnotations(obj)[JOURNAL_ENTRIES_ANNOTATIONS_KEY]

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
    def test_returns_journal_entries_in_newest_first_order(self, browser):
        self.login(self.regular_user, browser)
        self.clear_journal_entries(self.dossier)

        JournalManager(self.dossier).add_manual_entry('information', 'first')
        JournalManager(self.dossier).add_manual_entry('information', 'second')

        response = browser.open(
            self.dossier.absolute_url() + '/@journal',
            method='GET',
            headers=http_headers(),
        ).json

        entry_titles = [item.get('comments') for item in response.get('items')]
        self.assertEqual(['second', 'first'], entry_titles)

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

        person = create(Builder('person')
                        .having(firstname=u'H\xfcgo', lastname='Boss'))

        user = OgdsUserToContactAdapter.query.get(self.regular_user.id)

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            JournalManager(self.dossier).add_manual_entry(
                'information', 'is an agent',
                [person],
                [user],
                [self.document])

        response = browser.open(
            self.dossier.absolute_url() + '/@journal?b_size=2',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertDictEqual({
            u'actor_fullname': u'B\xe4rfuss K\xe4thi',
            u'actor_id': u'kathi.barfuss',
            u'comments': u'is an agent',
            u'related_documents': [{
                u'@id': self.document.absolute_url(),
                u'@type': u'opengever.document.document',
                u'checked_out': None,
                u'description': self.document.description,
                u'file_extension': u'.docx',
                u'is_leafnode': None,
                u'review_state': u'document-state-draft',
                u'title': self.document.title}],
            u'time': u'2017-10-16T00:00:00+00:00',
            u'title': u'Manual entry: Information'
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
            map(lambda item: item.get('comments'), response.json.get('items')))

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
            map(lambda item: item.get('comments'), response.json.get('items')))

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
            map(lambda item: item.get('comments'), response.json.get('items')))

    @browsing
    def test_can_search_by_title(self, browser):
        self.login(self.regular_user, browser)

        JournalManager(self.dossier).add_manual_entry('information', 'my information')
        JournalManager(self.dossier).add_manual_entry('phone-call', u'my phone c\xe4ll')

        response = browser.open(
            self.dossier, view='@journal', method='GET', headers=http_headers())

        self.assertEqual(19, response.json.get('items_total'))

        response = browser.open(
            self.dossier, view='@journal?search=Manual',
            method='GET', headers=http_headers())

        self.assertEqual(
            [u'Manual entry: Phone call', u'Manual entry: Information'],
            map(lambda item: item.get('title'), response.json.get('items')))
