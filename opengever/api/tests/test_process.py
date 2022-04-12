from datetime import date
from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_CURRENT_USER_ID
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_RESPONSIBLE_ID
from opengever.ogds.models.team import Team
from opengever.tasktemplates.interfaces import IFromParallelTasktemplate
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.tasktemplates.tasktemplatefolder import ProcessDataPreprocessor
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestProcessDataPreprocessor(IntegrationTestCase):

    def test_deadline_is_the_longest_deadline_of_children_plus_five(self):
        self.login(self.regular_user)
        data = {
            "process": {
                "items": [
                    {"deadline": date(2022, 03, 01)},
                    {"deadline": date(2022, 03, 05)},
                    {"deadline": date(2022, 03, 02)},
                ]
            }
        }
        processor = ProcessDataPreprocessor(self.dossier, data)
        with freeze(datetime(2022, 02, 01)):
            processor.recursive_set_deadlines()

        self.assertEqual(date(2022, 03, 10), data["process"]["deadline"])

    def test_deadline_at_least_today_plus_five(self):
        self.login(self.regular_user)
        data = {
            "process": {
                "items": [
                    {"deadline": date(2022, 03, 05)},
                    {"deadline": date(2022, 03, 01)},
                    {"deadline": date(2022, 03, 02)},
                ]
            }
        }
        processor = ProcessDataPreprocessor(self.dossier, data)
        with freeze(datetime(2022, 04, 01)):
            processor.recursive_set_deadlines()

        self.assertEqual(date(2022, 04, 06), data["process"]["deadline"])

    def test_recursive_deadline_propagation(self):
        self.login(self.regular_user)
        data = {
            "process": {
                "items": [
                    {"deadline": date(2022, 03, 01)},
                    {"items": [
                        {"deadline": date(2022, 03, 10)},
                        {"items": [
                            {"deadline": date(2022, 04, 2)},
                        ]},
                    ]},
                    {"items": [
                        {"deadline": date(2022, 03, 10)},
                        {"deadline": date(2022, 03, 05)},
                    ]},
                ]
            }
        }
        processor = ProcessDataPreprocessor(self.dossier, data)
        with freeze(datetime(2022, 02, 01)):
            processor.recursive_set_deadlines()

        expected_data = {
            "process": {
                "deadline": date(2022, 4, 17),
                "items": [
                    {"deadline": date(2022, 03, 01)},
                    {"deadline": date(2022, 4, 12),
                     "items": [
                        {"deadline": date(2022, 03, 10)},
                        {"deadline": date(2022, 4, 7),
                         "items": [
                            {"deadline": date(2022, 04, 2)},
                        ]},
                    ]},
                    {"deadline": date(2022, 03, 15),
                     "items": [
                        {"deadline": date(2022, 03, 10)},
                        {"deadline": date(2022, 03, 05)},
                    ]},
                ]
            }
        }

        self.assertEqual(expected_data, data)


class TestProcessPost(IntegrationTestCase):

    @browsing
    def test_create_simple_process(self, browser):
        self.login(self.regular_user, browser)
        data = {
            "related_documents": [],
            "start_immediately": False,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Assign userid",
                        "responsible": "fa:{}".format(self.regular_user.id),
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    }
                ]
            }
        }

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 02, 01)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        main_task = children['added'].pop()

        self.assertEqual(browser.json['@id'], main_task.absolute_url())
        self.assertEqual(u'New employee', main_task.title)
        self.assertEqual(self.regular_user.getId(), main_task.issuer)
        self.assertEqual(self.regular_user.getId(), main_task.responsible)
        self.assertEqual('fa', main_task.responsible_client)
        self.assertEqual('direct-execution', main_task.task_type)
        self.assertEqual('task-state-in-progress',
                         api.content.get_state(main_task))
        self.assertEqual(date(2022, 3, 6), main_task.deadline)

        subtasks = main_task.listFolderContents()
        self.assertEqual(1, len(subtasks))
        subtask = subtasks.pop()
        self.assertEqual(u'Assign userid', subtask.title)
        self.assertEqual(self.secretariat_user.id, subtask.issuer)
        self.assertEqual(self.regular_user.getId(), subtask.responsible)
        self.assertEqual('fa', subtask.responsible_client)
        self.assertEqual('task-state-planned',
                         api.content.get_state(subtask))
        self.assertEqual(date(2022, 3, 1), subtask.deadline)

    @browsing
    def test_create_nested_process(self, browser):
        self.login(self.regular_user, browser)
        data = {
            "related_documents": [],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Assign userid",
                        "responsible": "fa:{}".format(self.regular_user.id),
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
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

                    }
                ]
            }
        }

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 02, 01)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        main_task = children['added'].pop()

        subtasks = main_task.listFolderContents()
        self.assertEqual(2, len(subtasks))
        subtask = subtasks[0]
        subtask_container = subtasks[1]

        self.assertEqual(0, len(subtask.listFolderContents()))
        subsubtasks = subtask_container.listFolderContents()
        self.assertEqual(2, len(subsubtasks))
        subsubtask1, subsubtask2 = subsubtasks

        # Check data that is automatically set for the subtask container
        self.assertEqual(u'Training', subtask_container.title)
        self.assertEqual(self.regular_user.getId(), subtask_container.issuer)
        self.assertEqual(self.regular_user.getId(), subtask_container.responsible)
        self.assertEqual('fa', subtask_container.responsible_client)
        self.assertEqual('direct-execution', subtask_container.task_type)
        # Only state of main task is set to in progress
        self.assertEqual('task-state-in-progress',
                         api.content.get_state(main_task))
        self.assertEqual('task-state-open',
                         api.content.get_state(subtask_container))

        # Check deadline propagation
        self.assertEqual(date(2022, 3, 10), subsubtask1.deadline)
        self.assertEqual(date(2022, 3, 12), subsubtask2.deadline)
        self.assertEqual(date(2022, 3, 17), subtask_container.deadline)
        self.assertEqual(date(2022, 3, 1), subtask.deadline)
        self.assertEqual(date(2022, 3, 22), main_task.deadline)

        # check parallel and sequential interfaces
        self.assertTrue(IFromSequentialTasktemplate.providedBy(main_task))
        self.assertTrue(IFromSequentialTasktemplate.providedBy(subtask))
        self.assertTrue(IFromParallelTasktemplate.providedBy(subtask_container))
        self.assertTrue(IFromParallelTasktemplate.providedBy(subsubtask1))
        self.assertTrue(IFromParallelTasktemplate.providedBy(subsubtask2))

        # Check tasktemplatefolder predecessor
        # Not set for parallel process
        self.assertIsNone(subsubtask2.get_sql_object().get_previous_task())
        # Should be set for sequential but broken for now because the
        # subtask_container did not inherit the IFromSequentialTasktemplate
        # from the parent and is therefore not identified as sequential
        self.assertNotEqual(subtask.get_sql_object(),
                            subtask_container.get_sql_object().get_previous_task())

    @browsing
    def test_can_set_deadline_on_task_template_folder(self, browser):
        self.login(self.regular_user, browser)
        data = {
            "related_documents": [],
            "start_immediately": False,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "deadline": "2022-03-04",
                "items": [
                    {
                        "title": "Assign userid",
                        "responsible": "fa:{}".format(self.regular_user.id),
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    }
                ]
            }
        }

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 02, 01)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        main_task = children['added'].pop()
        self.assertEqual(date(2022, 3, 4), main_task.deadline)
        subtask = main_task.listFolderContents()[0]
        self.assertEqual(date(2022, 3, 1), subtask.deadline)

    @browsing
    def test_created_tasks_are_in_sync_with_sql_object(self, browser):
        self.login(self.regular_user, browser)
        data = {
            "related_documents": [],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Assign userid",
                        "responsible": "fa:{}".format(self.regular_user.id),
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
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

                    }
                ]
            }
        }

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 02, 01)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        tasks = [children['added'].pop()]
        tasks.extend(tasks[0].listFolderContents())
        tasks.extend(tasks[-1].listFolderContents())

        self.maxDiff = None
        self.assertEqual(5, len(tasks))

        def get_sql_data(task):
            model = task.get_sql_object()
            principals = sorted([(principal.principal, principal.task_id)
                                 for principal in model._principals])
            data = {
                "physical_path": model.physical_path,
                "title": model.title,
                "review_state": model.review_state,
                "_principals": principals,
            }
            return data

        for task in tasks:
            data_before_sync = get_sql_data(task)
            task.sync()
            data_after_sync = get_sql_data(task)
            self.assertDictEqual(data_before_sync, data_after_sync)

    @browsing
    def test_sets_related_documents_on_all_subtasks(self, browser):
        self.login(self.regular_user, browser)
        data = {
            'related_documents': [
                {
                    '@id': self.document.absolute_url()
                }
            ],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Assign userid",
                        "responsible": "fa:{}".format(self.regular_user.id),
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
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

                    }
                ]
            }
        }
        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 02, 01)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        main_task = children['added'].pop()
        subtasks = main_task.listFolderContents()
        self.assertEqual(2, len(subtasks))
        subtask, subtask_container = subtasks

        self.assertEqual(
            [self.document],
            [rel.to_object for rel in subtask.relatedItems])

        self.assertEqual(
            [self.document],
            [rel.to_object for rel in subtask_container.relatedItems])

        subsubtasks = subtask_container.listFolderContents()
        self.assertEqual(2, len(subtasks))
        for subsubtask in subsubtasks:
            self.assertEqual(
                [self.document],
                [rel.to_object for rel in subsubtask.relatedItems])

    @browsing
    def test_raises_bad_request_for_missing_main_fields(self, browser):
        self.login(self.regular_user, browser)
        data = {
            "start_immediately": True,
        }

        with browser.expect_http_error(400):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)
        self.assertEqual(u'Inputs not valid',
                         browser.json[u'translated_message'])

        self.assertItemsEqual(
            [{u'field': u'process',
              u'translated_message': u'None',
              u'type': u'process'}],
            browser.json[u'additional_metadata']['fields'])

    @browsing
    def test_raises_bad_request_for_missing_field_in_subtask(self, browser):
        self.login(self.regular_user, browser)
        data = {
            "related_documents": [],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Assign userid",
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    }
                ]
            }
        }

        with browser.expect_http_error(400):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(u'Inputs not valid',
                         browser.json[u'translated_message'])

        self.assertItemsEqual(
            [{u'field': u'responsible_client',
              u'translated_message': u'None',
              u'type': u'responsible_client'},
             {u'field': u'responsible',
              u'translated_message': u'None',
              u'type': u'responsible'}],
            browser.json[u'additional_metadata']['fields'])

    @browsing
    def test_respects_start_immediately_flag(self, browser):
        self.login(self.regular_user, browser)
        data = {
            "related_documents": [],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Assign userid",
                        "responsible": "fa:{}".format(self.regular_user.id),
                        "issuer": self.secretariat_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    },
                    {
                        "title": "Assign desk",
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
        self.assertEquals('task-state-in-progress',
                          api.content.get_state(main_task))
        subtask_1, subtask_2 = main_task.listFolderContents()
        self.assertEquals('task-state-open',
                          api.content.get_state(subtask_1))
        self.assertEquals('task-state-planned',
                          api.content.get_state(subtask_2))

        data["start_immediately"] = False
        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 02, 01)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        main_task = children['added'].pop()
        self.assertEquals('task-state-in-progress',
                          api.content.get_state(main_task))
        subtask_1, subtask_2 = main_task.listFolderContents()
        self.assertEquals('task-state-planned',
                          api.content.get_state(subtask_1))
        self.assertEquals('task-state-planned',
                          api.content.get_state(subtask_2))

    @browsing
    def test_handles_interactive_actors(self, browser):
        self.login(self.regular_user, browser)
        data = {
            "related_documents": [],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Assign userid",
                        "responsible": INTERACTIVE_ACTOR_RESPONSIBLE_ID,
                        "issuer": INTERACTIVE_ACTOR_CURRENT_USER_ID,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    },
                    {
                        "title": "Assign desk",
                        "responsible": INTERACTIVE_ACTOR_CURRENT_USER_ID,
                        "issuer": INTERACTIVE_ACTOR_RESPONSIBLE_ID,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    }
                ]
            }
        }

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 02, 01)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        main_task = children['added'].pop()
        subtasks = main_task.listFolderContents()
        self.assertEqual(2, len(subtasks))
        subtask1, subtask2 = subtasks
        self.assertEqual(subtask1.responsible, self.dossier_responsible.id)
        self.assertEqual(subtask1.responsible_client, 'fa')
        self.assertEqual(subtask1.issuer, self.regular_user.id)
        self.assertEqual(subtask2.responsible, self.regular_user.id)
        self.assertEqual(subtask2.responsible_client, 'fa')
        self.assertEqual(subtask2.issuer, self.dossier_responsible.id)

    @browsing
    def test_handles_teams_and_inbox_as_task_responsible(self, browser):
        self.login(self.regular_user, browser)
        team = Team.get_by(groupid='projekt_a')
        team_id = 'team:{}'.format(team.team_id)
        inbox_id = 'inbox:fa'
        data = {
            "related_documents": [],
            "start_immediately": True,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Assign userid",
                        "responsible": team_id,
                        "issuer": self.regular_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    },
                    {
                        "title": "Assign desk",
                        "responsible": inbox_id,
                        "issuer": self.regular_user.id,
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": False,
                    }
                ]
            }
        }

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 02, 01)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        main_task = children['added'].pop()
        subtasks = main_task.listFolderContents()
        self.assertEqual(2, len(subtasks))
        subtask1, subtask2 = subtasks
        self.assertEqual(subtask1.responsible, team_id)
        self.assertEqual(subtask1.responsible_client, 'fa')
        self.assertEqual(subtask2.responsible, inbox_id)
        self.assertEqual(subtask2.responsible_client, 'fa')
