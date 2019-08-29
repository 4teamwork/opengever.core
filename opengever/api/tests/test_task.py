from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone.restapi.serializer.converters import json_compatible


class TestTaskSerialization(IntegrationTestCase):

    @browsing
    def test_task_contains_a_list_of_responses(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)

        responses = browser.json['responses']
        self.assertEquals(2, len(responses))
        self.assertEquals(
            {u'added_objects': [{u'@id': self.subtask.absolute_url(),
                                 u'@type': u'opengever.task.task',
                                 u'description': u'',
                                 u'review_state': u'task-state-resolved',
                                 u'title': self.subtask.title}],
             u'changes': [],
             u'creator': self.dossier_responsible.id,
             u'date': json_compatible(self.subtask.created()),
             u'date_of_completion': None,
             u'related_items': [],
             u'text': u'',
             u'transition': u'transition-add-subtask'},
            responses[0])

    @browsing
    def test_task_response_contains_changes(self, browser):
        # Modify deadline to have a response containing field changes
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.task)
        browser.click_on('task-transition-modify-deadline')
        browser.fill({'Response': 'Nicht mehr dringend',
                      'New Deadline': '1.1.2023'})
        browser.click_on('Save')

        self.login(self.regular_user, browser=browser)
        browser.open(self.task, method="GET", headers=self.api_headers)

        response = browser.json['responses'][-1]
        self.assertEquals(
            self.dossier_responsible.id, response['creator'].get('token'))
        self.assertEquals(
            u'task-transition-modify-deadline', response['transition'])
        self.assertEquals(
            [{u'id': u'deadline', u'name': u'Deadline',
              u'after': u'2023-01-01', u'before': u'2016-11-01'}],
            response['changes'])

    @browsing
    def test_response_key_contains_empty_list_for_task_without_responses(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.inbox_task, method="GET", headers=self.api_headers)
        self.assertEquals([], browser.json['responses'])

    @browsing
    def test_fowardings_contains_a_list_of_responses(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(
            self.inbox_forwarding, method="GET", headers=self.api_headers)

        self.assertEquals(
            [{u'added_objects': [{
                u'@id': u'http://nohost/plone/eingangskorb/forwarding-1/document-13',
                u'@type': u'opengever.document.document',
                u'description': u'',
                u'review_state': u'document-state-draft',
                u'title': u'Dokument im Eingangsk\xf6rbliweiterleitung'}],
              u'changes': [],
              u'creator': u'nicole.kohler',
              u'date': u'2016-08-31T10:07:33+00:00',
              u'date_of_completion': None,
              u'related_items': [],
              u'text': u'',
              u'transition': u'transition-add-document'}],
            browser.json['responses'])
