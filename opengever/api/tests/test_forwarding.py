from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
import json


class TestForwardingSerialization(SolrIntegrationTestCase):

    maxDiff = None

    @browsing
    def test_fowardings_contains_a_list_of_responses(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(
            self.inbox_forwarding, method="GET", headers=self.api_headers)
        self.assertEquals(
            [{u'@id': u'http://nohost/plone/eingangskorb/eingangskorb_fa/forwarding-1/@responses/1472634573000000',
              u'response_id': 1472634573000000,
              u'response_type': u'default',
              u'added_objects': [{
                u'@id': u'http://nohost/plone/eingangskorb/eingangskorb_fa/forwarding-1/document-13',
                u'@type': u'opengever.document.document',
                u'checked_out': None,
                u'description': u'',
                u'file_extension': u'.txt',
                u'is_leafnode': None,
                u'review_state': u'document-state-draft',
                u'title': u'Dokument im Eingangsk\xf6rbliweiterleitung'}],
              u'approved_documents': [],
              u'changes': [],
              u'creator': {
                  u'token': u'nicole.kohler',
                  u'title': u'Kohler Nicole'},
              u'created': u'2016-08-31T11:09:33',
              u'related_items': [],
              u'text': u'',
              u'mimetype': u'',
              u'modified': None,
              u'modifier': None,
              u'additional_data':{},
              u'subtask': None,
              u'successor_oguid': u'',
              u'rendered_text': u'',
              u'transition': u'transition-add-document'}],
            browser.json['responses'])

    @browsing
    def test_containing_dossier_for_inbox_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)
        browser.open(self.inbox_forwarding, method="GET", headers=self.api_headers)
        self.maxDiff = None
        self.assertDictEqual(
            {
                u'@id': u'http://nohost/plone/eingangskorb/eingangskorb_fa',
                u'@type': u'opengever.inbox.inbox',
                u'description': u'',
                u'is_leafnode': None,
                u'review_state': u'inbox-state-default',
                u'title': u'Eingangsk\xf6rbli FA',
            },
            browser.json['containing_dossier']
        )

    @browsing
    def test_forwarding_task_type_serialization_provides_object(self, browser):
        self.login(self.secretariat_user, browser=browser)
        browser.open(self.inbox_forwarding, method="GET", headers=self.api_headers)

        self.assertEqual(
            {u'token': u'forwarding_task_type', u'title': u'Forwarding'},
            browser.json['task_type']
        )

    @browsing
    def test_fowarding_contains_creator(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(
            self.inbox_forwarding, method="GET", headers=self.api_headers)

        self.assertEqual(self.administrator.getId(),
                         browser.json['creator']['identifier'])


class TestForwardingTransitions(IntegrationTestCase):

    @browsing
    def test_reassign_forwarding_with_combined_responsible_value(self, browser):
        self.login(self.secretariat_user, browser=browser)

        self.assertEqual('fa', self.inbox_forwarding.responsible_client)
        self.assertEqual('kathi.barfuss', self.inbox_forwarding.responsible)

        data = {
            'responsible': {
                'token': 'rk:james.bond',
                'title': u'Ratskanzlei: James Bond'
            }
        }
        browser.open(self.inbox_forwarding.absolute_url() + '/@workflow/forwarding-transition-reassign',
                     json.dumps(data),
                     method="POST", headers=self.api_headers)

        self.assertEqual('rk', self.inbox_forwarding.responsible_client)
        self.assertEqual('james.bond', self.inbox_forwarding.responsible)

    @browsing
    def test_reassign_forwarding_without_combined_responsible_value(self, browser):
        self.login(self.secretariat_user, browser=browser)

        self.assertEqual('fa', self.inbox_forwarding.responsible_client)
        self.assertEqual('kathi.barfuss', self.inbox_forwarding.responsible)

        data = {
            'responsible': 'james.bond',
            'responsible_client': 'rk',
        }
        browser.open(self.inbox_forwarding.absolute_url() + '/@workflow/forwarding-transition-reassign',
                     json.dumps(data),
                     method="POST", headers=self.api_headers)

        self.assertEqual('rk', self.inbox_forwarding.responsible_client)
        self.assertEqual('james.bond', self.inbox_forwarding.responsible)
