from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase


class TestTaskSuccessorsGet(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_get_successors_for_task(self, browser):
        self.login(self.regular_user, browser=browser)
        self.register_successor(self.task, self.expired_task)
        browser.open(
            self.task, view="@successors", method="GET",
            headers=self.api_headers
        )

        expected = {
            '@id': u'{}/@successors'.format(self.task.absolute_url()),
            'items': [{
                u'@id': self.expired_task.absolute_url(),
                u'@type': u'opengever.task.task',
                u'oguid': Oguid.for_object(self.expired_task).id,
                u'review_state': u'task-state-resolved',
                u'task_type': u'For your review',
                u'title': u'Vertr\xe4ge abschliessen',
            }]
        }
        actual = browser.json
        self.assertIn('task_id', actual['items'][0])
        del actual['items'][0]['task_id']
        self.assertEqual(expected, actual)

    @browsing
    def test_get_successors_for_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)
        self.register_successor(self.inbox_forwarding, self.expired_task)
        browser.open(
            self.inbox_forwarding, view="@successors", method="GET",
            headers=self.api_headers
        )

        expected = {
            '@id': u'{}/@successors'.format(self.inbox_forwarding.absolute_url()),
            'items': [{
                u'@id': self.expired_task.absolute_url(),
                u'@type': u'opengever.task.task',
                u'oguid': Oguid.for_object(self.expired_task).id,
                u'review_state': u'task-state-resolved',
                u'task_type': u'For your review',
                u'title': u'Vertr\xe4ge abschliessen',
            }]
        }
        actual = browser.json
        self.assertIn('task_id', actual['items'][0])
        del actual['items'][0]['task_id']
        self.assertEqual(expected, actual)

    @browsing
    def test_get_successors_for_task_without_successors(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.task, view="@successors", method="GET",
            headers=self.api_headers
        )

        expected = {
            '@id': u'{}/@successors'.format(self.task.absolute_url()),
            'items': [],
        }
        actual = browser.json
        self.assertEqual(expected, actual)

    @browsing
    def test_get_task_with_successors_expansion(self, browser):
        self.login(self.regular_user, browser=browser)
        self.register_successor(self.task, self.expired_task)
        browser.open(
            self.task, view="?expand=successors", method="GET",
            headers=self.api_headers
        )

        self.assertIn('successors', browser.json['@components'])
        expected = {
            '@id': u'{}/@successors'.format(self.task.absolute_url()),
            'items': [{
                u'@id': self.expired_task.absolute_url(),
                u'@type': u'opengever.task.task',
                u'oguid': Oguid.for_object(self.expired_task).id,
                u'review_state': u'task-state-resolved',
                u'task_type': u'For your review',
                u'title': u'Vertr\xe4ge abschliessen',
            }]
        }
        actual = browser.json['@components']['successors']
        self.assertIn('task_id', actual['items'][0])
        del actual['items'][0]['task_id']
        self.assertEqual(expected, actual)
