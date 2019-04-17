from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.journal.entry import ManualJournalEntry
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

        with browser.expect_http_error(400):
            browser.open(
                self.dossier.absolute_url() + '/@journal',
                data=json.dumps(payload),
                method='POST',
                headers=http_headers(),
            )

        bad_document_urls = [
            "https://not-existing",
            "http://nohost/plone/not-existing",
            self.dossier.absolute_url()
        ]

        self.assertEqual(
            {"message": "Could not lookup the following documents: {}".format(
                ', '.join(bad_document_urls)),
             "type": "BadRequest"},
            browser.json)


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

        ManualJournalEntry(self.dossier, 'information', 'first', [], [], []).save()
        ManualJournalEntry(self.dossier, 'information', 'second', [], [], []).save()

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

        ManualJournalEntry(self.dossier, 'information', 'first', [], [], []).save()
        ManualJournalEntry(self.dossier, 'information', 'second', [], [], []).save()

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

        ManualJournalEntry(self.dossier, 'information', 'first', [], [], []).save()
        ManualJournalEntry(self.dossier, 'information', 'second', [], [], []).save()
        ManualJournalEntry(self.dossier, 'information', 'third', [], [], []).save()

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
            ManualJournalEntry(self.dossier, 'information', 'is an agent',
                               [person],
                               [user],
                               [self.document]).save()

        response = browser.open(
            self.dossier.absolute_url() + '/@journal?b_size=2',
            method='GET',
            headers=http_headers(),
        ).json

        self.assertDictEqual({
            'actor_fullname': u'B\xe4rfuss K\xe4thi',
            'actor_id': u'kathi.barfuss',
            'comments': u'is an agent',
            'time': u'2017-10-16T00:00:00+00:00',
            'title': u'Manual entry: Information'
            }, response.get('items')[0])

