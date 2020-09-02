from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase


class TestGlobalIndexGet(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_lists_all_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@globalindex?sort_on=title',
                     headers=self.api_headers)

        self.assertEqual(15, browser.json['items_total'])
        self.assertEqual(15, len(browser.json['items']))
        self.assertEqual(
            {u'@id': self.inbox_task.absolute_url(),
             u'@type': u'opengever.task.task',
             u'assigned_org_unit': u'fa',
             u'containing_dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'created': u'2016-08-31T18:27:33',
             u'deadline': u'2020-01-01',
             u'is_private': True,
             u'is_subtask': False,
             u'issuer': u'robert.ziegler',
             u'issuer_fullname': u'Ziegler Robert',
             u'issuing_org_unit': u'fa',
             u'modified': u'2016-08-31T18:27:33',
             u'oguid': str(Oguid.for_object(self.inbox_task)),
             u'predecessor_id': None,
             u'responsible': u'inbox:fa',
             u'responsible_fullname': u'Inbox: Finanz\xe4mt',
             u'review_state': u'task-state-in-progress',
             u'task_id': 14,
             u'task_type': u'For direct execution',
             u'title': u're: Diskr\xe4te Dinge',
             },
            browser.json['items'][0])

        # default row size is 25
        self.assertIsNone(browser.json['batching'])

    @browsing
    def test_respect_batching_parameters(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@globalindex?b_size=3',
                     headers=self.api_headers)

        self.assertEqual(15, browser.json['items_total'])
        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(0, browser.json['b_start'])
        self.assertEqual(3, browser.json['b_size'])
        self.assertEqual(
            {u'@id': u'http://nohost/plone/@globalindex?b_size=3',
             u'first': u'http://nohost/plone/@globalindex?b_start=0&b_size=3',
             u'last': u'http://nohost/plone/@globalindex?b_start=12&b_size=3',
             u'next': u'http://nohost/plone/@globalindex?b_start=3&b_size=3'},
            browser.json['batching'])

    @browsing
    def test_respect_sort_parameter(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@globalindex?sort_on=title&b_size=3',
                     headers=self.api_headers)

        self.assertEqual(
            [u're: Diskr\xe4te Dinge',
             u'Vorstellungsrunde bei anderen Mitarbeitern',
             u'Vertr\xe4ge abschliessen'],
            [item['title'] for item in browser.json['items']])

        browser.open(
            self.portal,
            view='@globalindex?sort_on=title&b_size=3&sort_order=ascending',
            headers=self.api_headers)

        self.assertEqual(
            [u'Arbeitsplatz vorbereiten',
             u'Diskr\xe4te Dinge',
             u'Ein notwendiges \xdcbel'],
            [item['title'] for item in browser.json['items']])

    @browsing
    def test_fallback_to_default_sort_if_sort_on_does_not_exist(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@globalindex?sort_on=notexisting&b_size=3',
                     headers=self.api_headers)

        self.assertEqual(15, browser.json['items_total'])
        self.assertEqual(u'Ein notwendiges \xdcbel', browser.json['items'][0]['title'])
        self.assertEqual(u'2016-08-31T20:25:33', browser.json['items'][0]['modified'])

    @browsing
    def test_filter_by_single_value(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@globalindex?filters.responsible:record={}'.format(
            self.regular_user.id)
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(
            set([self.regular_user.id]),
            set([item['responsible'] for item in browser.json['items']]))

        self.assertEqual(12, browser.json['items_total'])
        self.assertEqual(12, len(browser.json['items']))

    @browsing
    def test_filter_by_value_list(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@globalindex?filters.review_state:record:list=task-state-open&filters.review_state:record:list=task-state-in-progress'

        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(
            set(['task-state-in-progress', 'task-state-open']),
            set([item['review_state'] for item in browser.json['items']]))

        self.assertEqual(9, browser.json['items_total'])
        self.assertEqual(9, len(browser.json['items']))

    @browsing
    def test_handles_search_queries(self, browser):
        self.login(self.regular_user, browser=browser)

        view = u'@globalindex'
        browser.open(self.portal, view=view.format(''), headers=self.api_headers)
        self.assertEqual(15, browser.json['items_total'])
        all_tasks = browser.json.get('items')

        search_term = u'Vertr\xe4ge'
        view = u'@globalindex?search={}'.format(search_term)
        browser.open(self.portal, view=view, headers=self.api_headers)
        self.assertEqual(1, browser.json['items_total'])
        self.assertEqual(
            filter(lambda task: u'Vertr\xe4ge' in task.get('title'), all_tasks),
            browser.json['items'])

    @browsing
    def test_query_is_restricted(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal, view='@globalindex', headers=self.api_headers)
        self.assertEqual(15, browser.json['items_total'])

        with self.login(self.secretariat_user, browser=browser):
            browser.open(self.portal, view='@globalindex', headers=self.api_headers)
            self.assertEqual(14, browser.json['items_total'])

    @browsing
    def test_forwarding_task_type_is_translated(self, browser):
        self.login(self.regular_user, browser=browser)

        search_term = u'F\xf6rw\xe4rding'
        view = u'@globalindex?search={}'.format(search_term)
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(1, browser.json['items_total'])
        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual(u'Forwarding', browser.json['items'][0]['task_type'])

    @browsing
    def test_adds_portal_type_to_globalindex_items(self, browser):
        self.login(self.regular_user, browser=browser)

        view = (
            '@globalindex?filters.task_type:record:list=information'
            '&filters.task_type:record:list=forwarding_task_type'
            '&sort_on=title'
        )
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(2, browser.json['items_total'])
        self.assertEqual(2, len(browser.json['items']))
        items = browser.json['items']
        self.assertEqual(items[0]['@type'], u'opengever.task.task')
        self.assertEqual(items[1]['@type'], u'opengever.inbox.forwarding')

