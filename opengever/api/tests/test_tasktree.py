from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import SolrIntegrationTestCase
import json


class TestTaskTree(SolrIntegrationTestCase):

    @browsing
    def test_get_tasktree_for_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.task, view="@tasktree", method="GET", headers=self.api_headers)
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1/@tasktree',
                u'children': [
                    {
                        u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1',
                        u'@type': u'opengever.task.task',
                        u'children': [{u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1/task-2',
                                       u'@type': u'opengever.task.task',
                                       u'children': [],
                                       u'is_task_addable': False,
                                       u'is_task_addable_before': False,
                                       u'review_state': u'task-state-resolved',
                                       u'title': u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen'}],
                        u'is_task_addable': False,
                        u'is_task_addable_before': False,
                        u'review_state': u'task-state-in-progress',
                        u'title': u'Vertragsentwurf \xdcberpr\xfcfen'}]},
            browser.json
        )

    @browsing
    def test_addable_task_attributes(self, browser):
        self.login(self.regular_user, browser=browser)
        data = {
            "related_documents": [],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Workout",
                        "sequence_type": "sequential",
                        "items": [
                            {
                                "title": "Present Gever",
                                "responsible": "fa:{}".format(self.regular_user.id),
                                "issuer": self.dossier_responsible.id,
                                "deadline": "2022-03-10",
                                "task_type": "direct-execution",
                                "is_private": False,
                            },
                            {
                                "title": "Present Teamraum",
                                "responsible": "fa:{}".format(self.workspace_admin.id),
                                "issuer": self.dossier_responsible.id,
                                "deadline": "2022-03-12",
                                "task_type": "direct-execution",
                                "is_private": False,
                            },
                        ]

                    },
                    {
                        "title": "Training",
                        "sequence_type": "parallel",
                        "items": [
                            {
                                "title": "Present Gever",
                                "responsible": "fa:{}".format(self.regular_user.id),
                                "issuer": self.dossier_responsible.id,
                                "deadline": "2022-03-10",
                                "task_type": "direct-execution",
                                "is_private": False,
                            },
                            {
                                "title": "Present Teamraum",
                                "responsible": "fa:{}".format(self.workspace_admin.id),
                                "issuer": self.dossier_responsible.id,
                                "deadline": "2022-03-12",
                                "task_type": "direct-execution",
                                "is_private": False,
                            },
                        ]

                    },
                    {
                        "title": "Assign userid",
                        "responsible": "fa:{}".format(self.regular_user.id),
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    },
                ]
            }
        }
        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 02, 01)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        main_task = children['added'].pop()
        self.commit_solr()

        browser.open(main_task, view="@tasktree", method="GET", headers=self.api_headers)

        self.assertTrue(browser.json['children'][0]['is_task_addable'],
                        "Tasks should be addable on a sequential main task")

        self.assertTrue(browser.json['children'][0]['children'][0]['is_task_addable'],
                        "Tasks should be addable on sequential subtask containers")

        self.assertFalse(browser.json['children'][0]['children'][1]['is_task_addable'],
                         "Tasks should not be addable on parallel subtask containers")

        self.assertFalse(browser.json['children'][0]['children'][2]['is_task_addable'],
                         "Tasks should not be addable on a subtask")

        self.assertFalse(browser.json['children'][0]['is_task_addable_before'],
                         "No task should be addable before the main task")

        self.assertFalse(browser.json['children'][0]['children'][0]['is_task_addable_before'],
                         "Tasks should not be addable before an open task of a task sequence")

        self.assertTrue(browser.json['children'][0]['children'][1]['is_task_addable_before'],
                        "Tasks should be addable before planned tasks of a task sequence")

        self.assertFalse(browser.json['children'][0]['children'][1]['children'][0]['is_task_addable_before'],
                         "Tasks should not be addable before tasks within parallel tasks")

    @browsing
    def test_sequential_tasks_are_sorted_on_obj_position_in_parent(self, browser):
        self.login(self.regular_user, browser=browser)
        subtasks = [self.seq_subtask_3, self.seq_subtask_1, self.seq_subtask_2]
        self.sequential_task.set_tasktemplate_order(subtasks)
        self.commit_solr()

        browser.open(self.sequential_task, view='@tasktree', method='GET', headers=self.api_headers)
        self.assertEqual(
            [self.seq_subtask_3.absolute_url(),
             self.seq_subtask_1.absolute_url(),
             self.seq_subtask_2.absolute_url()],
            [item['@id'] for item in browser.json['children'][0]['children']])

    @browsing
    def test_sequential_subtasks_are_sorted_correctly_in_nested_parallel_and_sequential_tasks(self, browser):
        self.login(self.regular_user, browser=browser)
        data = {
            "related_documents": [],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "parallel",
                "items": [
                    {
                        "title": "Workout",
                        "sequence_type": "sequential",
                        "items": [
                            {
                                "title": "Present Gever",
                                "responsible": "fa:{}".format(self.regular_user.id),
                                "issuer": self.dossier_responsible.id,
                                "deadline": "2022-03-10",
                                "task_type": "direct-execution",
                                "is_private": False,
                            },
                            {
                                "title": "Present Teamraum",
                                "responsible": "fa:{}".format(self.workspace_admin.id),
                                "issuer": self.dossier_responsible.id,
                                "deadline": "2022-03-12",
                                "task_type": "direct-execution",
                                "is_private": False,
                            },
                        ]

                    },
                    {
                        "title": "Assign userid",
                        "responsible": "fa:{}".format(self.regular_user.id),
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    },
                ]
            }
        }
        with self.observe_children(self.dossier) as children:
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        main_task = children['added'].pop()
        subtask1, subtask2 = main_task.contentValues()
        sequential1, sequential2 = subtask1.contentValues()

        subtask1.set_tasktemplate_order([sequential2, sequential1])

        self.commit_solr()
        browser.open(main_task, view="@tasktree", method="GET", headers=self.api_headers)

        # Ordered according to position in parent
        self.assertEqual(
            [sequential2.absolute_url(),
             sequential1.absolute_url()],
            [item['@id'] for item in browser.json['children'][0]['children'][0]['children']])

    @browsing
    def test_parallel_subtasks_are_sorted_correctly_in_nested_parallel_and_sequential_tasks(self, browser):
        self.login(self.regular_user, browser=browser)
        data = {
            "related_documents": [],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Training",
                        "sequence_type": "parallel",
                        "items": [
                            {
                                "title": "Present Gever",
                                "responsible": "fa:{}".format(self.regular_user.id),
                                "issuer": self.dossier_responsible.id,
                                "deadline": "2022-03-10",
                                "task_type": "direct-execution",
                                "is_private": False,
                            },
                            {
                                "title": "Present Teamraum",
                                "responsible": "fa:{}".format(self.workspace_admin.id),
                                "issuer": self.dossier_responsible.id,
                                "deadline": "2022-03-12",
                                "task_type": "direct-execution",
                                "is_private": False,
                            },
                        ]

                    },
                    {
                        "title": "Assign userid",
                        "responsible": "fa:{}".format(self.regular_user.id),
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    },
                ]
            }
        }
        with self.observe_children(self.dossier) as children:
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        main_task = children['added'].pop()
        subtask1, subtask2 = main_task.contentValues()
        parallel1, parallel2 = subtask1.contentValues()

        subtask2.set_tasktemplate_order([parallel2, parallel1])

        self.commit_solr()
        browser.open(main_task, view="@tasktree", method="GET", headers=self.api_headers)

        # Ordered according to creation date
        self.assertEqual(
            [parallel1.absolute_url(),
             parallel2.absolute_url()],
            [item['@id'] for item in browser.json['children'][0]['children'][0]['children']])

    @browsing
    def test_get_task_with_tasktree_expansion(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.task, view="?expand=tasktree", method="GET",
            headers=self.api_headers)
        self.assertIn('tasktree', browser.json['@components'])
        self.assertEqual(
            browser.json['@components']['tasktree']['children'],
            [
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1',
                    u'@type': u'opengever.task.task',
                    u'children': [{u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1/task-2',
                                   u'@type': u'opengever.task.task',
                                   u'children': [],
                                   u'is_task_addable': False,
                                   u'is_task_addable_before': False,
                                   u'review_state': u'task-state-resolved',
                                   u'title': u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen'}],
                    u'is_task_addable': False,
                    u'is_task_addable_before': False,
                    u'review_state': u'task-state-in-progress',
                    u'title': u'Vertragsentwurf \xdcberpr\xfcfen'
                }
            ]
        )

    @browsing
    def test_get_tasktree_with_no_permissions_on_main_task_returns_empty_dict(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        subtask = create(
            Builder('task')
            .within(self.task_in_protected_dossier)
            .titled(u'Unteraufgabe')
            .having(
                responsible_client='fa',
                responsible=self.dossier_manager.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='correction'
            )
            .in_state('task-state-in-progress')
        )

        browser.open(
            subtask, view="@tasktree", method="GET", headers=self.api_headers)

        self.assertEqual(
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-17/task-14/task-15/@tasktree',
             u'children': [{u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-17/task-14',
                            u'@type': u'opengever.task.task',
                            u'children': [],
                            u'is_task_addable': False,
                            u'is_task_addable_before': False,
                            u'review_state': u'task-state-in-progress',
                            u'title': u'Ein notwendiges \xdcbel'}]},
            browser.json
        )

        self.login(self.dossier_manager, browser=browser)
        browser.open(
            subtask, view="@tasktree", method="GET", headers=self.api_headers)
        self.assertEqual(
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-17/task-14/task-15/@tasktree',
             u'children': []},
            browser.json
        )
