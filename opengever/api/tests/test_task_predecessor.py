from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase


class TestTaskPredecessorGet(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_get_predecessor_for_task(self, browser):
        self.login(self.regular_user, browser=browser)
        self.register_successor(self.task, self.expired_task)
        browser.open(
            self.expired_task, view="@predecessor", method="GET",
            headers=self.api_headers
        )
        expected = {
            '@id': u'{}/@predecessor'.format(self.expired_task.absolute_url()),
            'item': {
                u'@id': self.task.absolute_url(),
                u'@type': u'opengever.task.task',
                u'oguid': Oguid.for_object(self.task).id,
                u'review_state': u'task-state-in-progress',
                u'task_type': u'For your review',
                u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
            }
        }
        actual = browser.json
        self.assertIn('task_id', actual['item'])
        del actual['item']['task_id']
        self.assertEqual(expected, actual)

    @browsing
    def test_get_predecessor_for_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)
        self.register_successor(self.task, self.inbox_forwarding)
        browser.open(
            self.inbox_forwarding, view="@predecessor", method="GET",
            headers=self.api_headers
        )
        expected = {
            '@id': u'{}/@predecessor'.format(self.inbox_forwarding.absolute_url()),
            'item': {
                u'@id': self.task.absolute_url(),
                u'@type': u'opengever.task.task',
                u'oguid': Oguid.for_object(self.task).id,
                u'review_state': u'task-state-in-progress',
                u'task_type': u'For your review',
                u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
            }
        }
        actual = browser.json
        self.assertIn('task_id', actual['item'])
        del actual['item']['task_id']
        self.assertEqual(expected, actual)

    @browsing
    def test_get_predecessor_for_task_without_predecessor(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.expired_task, view="@predecessor", method="GET",
            headers=self.api_headers
        )
        expected = {
            '@id': u'{}/@predecessor'.format(self.expired_task.absolute_url()),
            'item': None,
        }
        actual = browser.json
        self.assertEqual(expected, actual)

    @browsing
    def test_get_task_with_predecessor_expansion(self, browser):
        self.login(self.regular_user, browser=browser)
        self.register_successor(self.task, self.expired_task)
        browser.open(
            self.expired_task, view="?expand=predecessor", method="GET",
            headers=self.api_headers
        )

        self.assertIn('predecessor', browser.json['@components'])
        expected = {
            '@id': u'{}/@predecessor'.format(self.expired_task.absolute_url()),
            'item': {
                u'@id': self.task.absolute_url(),
                u'@type': u'opengever.task.task',
                u'oguid': Oguid.for_object(self.task).id,
                u'review_state': u'task-state-in-progress',
                u'task_type': u'For your review',
                u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
            }
        }
        actual = browser.json['@components']['predecessor']
        self.assertIn('task_id', actual['item'])
        del actual['item']['task_id']
        self.assertEqual(expected, actual)
