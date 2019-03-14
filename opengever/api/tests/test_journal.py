from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zope.annotation import IAnnotations
import json


class TestJournalPost(IntegrationTestCase):

    def journal_entries(self, obj):
        return IAnnotations(obj).get(JOURNAL_ENTRIES_ANNOTATIONS_KEY)

    @property
    def http_headers(self):
        return {'Accept': 'application/json',
                'Content-Type': 'application/json'}

    @browsing
    def test_add_journal_entry(self, browser):
        self.login(self.regular_user, browser)
        payload = {'comment': 'example comment', 'category': 'information',
                   'related_documents': [self.document.absolute_url()]}

        browser.open(
            self.dossier.absolute_url() + '/@journal',
            data=json.dumps(payload),
            method='POST',
            headers=self.http_headers,
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
                headers=self.http_headers,
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
                headers=self.http_headers,
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
                headers=self.http_headers,
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
