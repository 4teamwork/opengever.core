from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import AVOID_DUPLICATES_STRATEGY_PREDECESSOR_TASK
from opengever.globalindex.model.task import AVOID_DUPLICATES_STRATEGY_SUCCESSOR_TASK
from opengever.globalindex.model.task import Task
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.testing import IntegrationTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


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
             u'containing_subdossier': u'',
             u'created': u'2016-08-31T18:27:33',
             u'deadline': u'2020-01-01',
             u'is_completed': False,
             u'is_private': True,
             u'is_subtask': False,
             u'issuer': u'robert.ziegler',
             u'issuer_fullname': u'Ziegler Robert',
             u'issuer_actor': {
                u'@id': u'http://nohost/plone/@actors/robert.ziegler',
                u'identifier': u'robert.ziegler'},
             u'issuing_org_unit': u'fa',
             u'modified': u'2016-08-31T18:27:33',
             u'oguid': str(Oguid.for_object(self.inbox_task)),
             u'predecessor_id': None,
             u'responsible': u'inbox:fa',
             u'responsible_fullname': u'Inbox: Finanz\xe4mt',
             u'responsible_actor': {
                 u'@id': u'http://nohost/plone/@actors/inbox:fa',
                 u'identifier': u'inbox:fa'},
             u'review_state': u'task-state-in-progress',
             u'review_state_label': u'In progress',
             u'sequence_number': 13,
             u'task_id': 14,
             u'task_type': u'For direct execution',
             u'title': u're: Diskr\xe4te Dinge',
             },
            browser.json['items'][0])

        # default row size is 25
        self.assertIsNone(browser.json.get('batching'))

    @browsing
    def test_globalindex_has_containing_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)
        task_in_subdossier = create(Builder('task')
                                    .within(self.subdossier)
                                    .having(
                                        responsible_client='fa',
                                        responsible=self.regular_user.getId(),
                                        issuer=self.dossier_responsible.getId(),
                                    ))
        browser.open(self.portal, view='@globalindex?sort_on=created', headers=self.api_headers)
        self.assertEqual(self.subdossier.Title(), browser.json['items'][0]['containing_subdossier'])

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

        browser.open(self.portal, view='@globalindex?b_start=6&b_size=3',
                     headers=self.api_headers)
        self.assertEqual(
            {u'@id': u'http://nohost/plone/@globalindex?b_start=6&b_size=3',
             u'first': u'http://nohost/plone/@globalindex?b_start=0&b_size=3',
             u'last': u'http://nohost/plone/@globalindex?b_start=12&b_size=3',
             u'prev': u'http://nohost/plone/@globalindex?b_start=3&b_size=3',
             u'next': u'http://nohost/plone/@globalindex?b_start=9&b_size=3'},
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
    def test_ignores_sort_on_if_sort_on_does_not_exist(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.portal, view='@globalindex?sort_on=notexisting',
                     headers=self.api_headers)

        self.assertEqual(15, browser.json['items_total'])

        # items are sorted only by the unique_sort_on in that case
        task_ids = [item['task_id'] for item in browser.json['items']]
        self.assertEqual(task_ids, sorted(task_ids, reverse=True))

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
    def test_filter_by_excluding_value(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@globalindex?filters.-responsible:record={}'.format(
            self.regular_user.id)
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertNotIn(
            self.regular_user.id,
            [item['responsible'] for item in browser.json['items']],
        )

        self.assertEqual(3, browser.json['items_total'])
        self.assertEqual(3, len(browser.json['items']))

    @browsing
    def test_filter_by_responsible_includes_teams(self, browser):
        self.login(self.regular_user, browser=browser)

        create(
            Builder('task')
            .titled(u'Vertragsentw\xfcrfe 2018')
            .within(self.dossier)
            .having(
                task_type='direct-execution',
                responsible_client='fa',
                responsible='team:1',
            )
        )
        view = '@globalindex?filters.responsible:record={}'.format(
            self.regular_user.id)
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(
            set([self.regular_user.id, 'team:1']),
            set([item['responsible'] for item in browser.json['items']]))

        self.assertEqual(13, browser.json['items_total'])
        self.assertEqual(13, len(browser.json['items']))

    @browsing
    def test_filter_by_date(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@globalindex?filters.deadline:record=2020-01-01 TO 2020-12-31'
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(2, browser.json['items_total'])
        self.assertEqual(2, len(browser.json['items']))

        view = '@globalindex?filters.deadline:record=* TO 2019-01-01'
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(12, browser.json['items_total'])
        self.assertEqual(12, len(browser.json['items']))

        view = '@globalindex?filters.deadline:record=2018-01-01 TO *'
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(2, browser.json['items_total'])
        self.assertEqual(2, len(browser.json['items']))

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

        with self.login(self.dossier_responsible, browser=browser):
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

    @browsing
    def test_returns_requested_facets(self, browser):
        self.login(self.regular_user, browser=browser)
        view = (
            '@globalindex?'
            'facets:list=review_state&'
            'facets:list=task_type&'
            'facets:list=responsible'
        )
        headers = self.api_headers.copy()
        headers.update({'Accept-Language': 'de'})
        browser.open(self.portal, view=view, headers=headers)

        self.assertEqual(
            browser.json['facets'],
            {
                u'responsible': {
                    u'inbox:fa': {
                        u'count': 1,
                        u'label': u'Eingangskorb: Finanz\xe4mt',
                    },
                    u'kathi.barfuss': {
                        u'count': 12,
                        u'label': u'B\xe4rfuss K\xe4thi',
                    },
                    u'robert.ziegler': {
                        u'count': 2,
                        u'label': u'Ziegler Robert',
                    },
                },
                u'review_state': {
                    u'forwarding-state-open': {
                        u'count': 1,
                        u'label': u'Offen',
                    },
                    u'task-state-in-progress': {
                        u'count': 7,
                        u'label': u'In Arbeit',
                    },
                    u'task-state-open': {
                        u'count': 2,
                        u'label': u'Offen',
                    },
                    u'task-state-planned': {
                        u'count': 2,
                        u'label': u'Geplant',
                    },
                    u'task-state-resolved': {
                        u'count': 3,
                        u'label': u'Erledigt',
                    },
                },
                u'task_type': {
                    u'correction': {
                        u'count': 5,
                        u'label': u'Zur Pr\xfcfung / Korrektur',
                    },
                    u'direct-execution': {
                        u'count': 7,
                        u'label': u'Zur direkten Erledigung',
                    },
                    u'forwarding_task_type': {
                        u'count': 1,
                        u'label': u'Weiterleitung',
                    },
                    u'information': {
                        u'count': 1,
                        u'label': u'Zur Kenntnisnahme',
                    },
                },
            },
        )

    @browsing
    def test_use_successor_task_duplicate_strategy(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('admin_unit').id('unit-3').having(title='Remote'))
        create(Builder('admin_unit').id('unit-2').having(title='Remote'))
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IAdminUnitConfiguration)
        proxy.current_unit_id = u'unit-3'

        successor = Task.query.all()[0]
        predecessor = Task.query.all()[1]

        successor.predecessor = predecessor
        predecessor.admin_unit_id = 'unit-2'

        view = '@globalindex?duplicate_strategy={}'.format(
            AVOID_DUPLICATES_STRATEGY_SUCCESSOR_TASK)
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertIn(
            successor.id,
            [item['task_id'] for item in browser.json['items']])

        self.assertNotIn(
            predecessor.id,
            [item['task_id'] for item in browser.json['items']])

        self.assertEqual(14, browser.json['items_total'])

    @browsing
    def test_use_predecessor_task_duplicate_strategy(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('admin_unit').id('unit-3').having(title='Remote'))
        create(Builder('admin_unit').id('unit-2').having(title='Remote'))
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IAdminUnitConfiguration)
        proxy.current_unit_id = u'unit-3'

        successor = Task.query.all()[0]
        predecessor = Task.query.all()[1]

        successor.predecessor = predecessor
        predecessor.admin_unit_id = 'unit-2'

        view = '@globalindex?duplicate_strategy={}'.format(
            AVOID_DUPLICATES_STRATEGY_PREDECESSOR_TASK)
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertIn(
            predecessor.id,
            [item['task_id'] for item in browser.json['items']])

        self.assertNotIn(
            successor.id,
            [item['task_id'] for item in browser.json['items']])

        self.assertEqual(14, browser.json['items_total'])
