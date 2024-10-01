from datetime import date
from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_CURRENT_USER_ID
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_RESPONSIBLE_ID
from opengever.ogds.models.team import Team
from opengever.task import TASK_STATE_IN_PROGRESS
from opengever.task import TASK_STATE_OPEN
from opengever.task import TASK_STATE_PLANNED
from opengever.tasktemplates.interfaces import IContainParallelProcess
from opengever.tasktemplates.interfaces import IContainSequentialProcess
from opengever.tasktemplates.interfaces import IPartOfParallelProcess
from opengever.tasktemplates.interfaces import IPartOfSequentialProcess
from opengever.tasktemplates.tasktemplatefolder import ProcessDataPreprocessor
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestProcessDataPreprocessor(IntegrationTestCase):

    def test_deadline_is_the_longest_deadline_of_children_plus_five_workdays(self):
        self.login(self.regular_user)
        data = {
            "process": {
                "items": [
                    {"deadline": date(2022, 3, 1)},
                    {"deadline": date(2022, 3, 4)},  # Friday
                    {"deadline": date(2022, 3, 2)},
                ]
            }
        }
        processor = ProcessDataPreprocessor(self.dossier, data)
        with freeze(datetime(2022, 2, 1)):
            processor.recursive_set_deadlines()

        self.assertEqual(date(2022, 3, 11), data["process"]["deadline"])

    def test_deadline_at_least_today_plus_five_workdays(self):
        self.login(self.regular_user)
        data = {
            "process": {
                "items": [
                    {"deadline": date(2022, 3, 5)},
                    {"deadline": date(2022, 3, 1)},
                    {"deadline": date(2022, 3, 2)},
                ]
            }
        }
        processor = ProcessDataPreprocessor(self.dossier, data)

        # Friday
        with freeze(datetime(2022, 4, 1)):
            processor.recursive_set_deadlines()

        self.assertEqual(date(2022, 4, 8), data["process"]["deadline"])

    def test_recursive_deadline_propagation(self):
        self.login(self.regular_user)
        data = {
            "process": {
                "items": [
                    {"deadline": date(2022, 3, 1)},  # Tuesday
                    {"items": [
                        {"deadline": date(2022, 3, 10)},  # Thursday
                        {"items": [
                            {"deadline": date(2022, 4, 4)},  # Monday
                        ]},
                    ]},
                    {"items": [
                        {"deadline": date(2022, 3, 10)},  # Thursday
                        {"deadline": date(2022, 3, 4)},  # Friday
                    ]},
                ]
            }
        }
        processor = ProcessDataPreprocessor(self.dossier, data)
        with freeze(datetime(2022, 2, 1)):  # Tuesday
            processor.recursive_set_deadlines()

        expected_data = {
            "process": {
                "deadline": date(2022, 4, 25),  # Monday
                "items": [
                    {"deadline": date(2022, 3, 1)},
                    {"deadline": date(2022, 4, 18),  # Monday
                     "items": [
                        {"deadline": date(2022, 3, 10)},  # Thursday
                        {"deadline": date(2022, 4, 11),  # Monday
                         "items": [
                            {"deadline": date(2022, 4, 4)},  # Monday
                        ]},
                    ]},
                    {"deadline": date(2022, 3, 17),  # Thursday
                     "items": [
                        {"deadline": date(2022, 3, 10)},  # Thursday
                        {"deadline": date(2022, 3, 4)},  # Friday
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

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
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
        self.assertEqual(date(2022, 3, 8), main_task.deadline)

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
                            {
                                "title": "Other apps",
                                "sequence_type": "parallel",
                                "deadline": "2022-03-10",
                                "items": [
                                    {
                                        "title": "App 1",
                                        "responsible": "fa:{}".format(self.regular_user.id),
                                        "issuer": self.dossier_responsible.id,
                                        "deadline": "2022-03-10",
                                        "task_type": "direct-execution",
                                        "is_private": False,
                                    },
                                    {
                                        "title": "App 2",
                                        "responsible": "fa:{}".format(self.regular_user.id),
                                        "issuer": self.dossier_responsible.id,
                                        "deadline": "2022-03-10",
                                        "task_type": "direct-execution",
                                        "is_private": False,
                                    },
                                ]

                            }
                        ]

                    }
                ]
            }
        }

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        main_task = children['added'].pop()

        subtasks = main_task.listFolderContents()
        self.assertEqual(2, len(subtasks))
        subtask = subtasks[0]
        training_container = subtasks[1]

        self.assertEqual(0, len(subtask.listFolderContents()))
        training_container_items = training_container.listFolderContents()
        self.assertEqual(3, len(training_container_items))
        present_gever, present_teamraum, other_apps = training_container_items
        app_1, app_2 = other_apps.listFolderContents()

        # Check data that is automatically set for the subtask container
        self.assertEqual(u'Training', training_container.title)
        self.assertEqual(self.regular_user.getId(), training_container.issuer)
        self.assertEqual(self.regular_user.getId(), training_container.responsible)
        self.assertEqual('fa', training_container.responsible_client)
        self.assertEqual('direct-execution', training_container.task_type)
        # Only state of main task is set to in progress
        self.assertEqual('task-state-in-progress',
                         api.content.get_state(main_task))
        self.assertEqual('task-state-open', api.content.get_state(subtask))
        self.assertEqual('task-state-planned',
                         api.content.get_state(training_container))
        self.assertEqual('task-state-planned',
                         api.content.get_state(app_1))
        self.assertEqual('task-state-planned',
                         api.content.get_state(app_2))
        # Check deadline propagation

        self.assertEqual(date(2022, 3, 10), present_gever.deadline)
        self.assertEqual(date(2022, 3, 12), present_teamraum.deadline)
        self.assertEqual(date(2022, 3, 18), training_container.deadline)
        self.assertEqual(date(2022, 3, 1), subtask.deadline)
        self.assertEqual(date(2022, 3, 25), main_task.deadline)

        # check parallel and sequential interfaces
        self.assertTrue(IContainSequentialProcess.providedBy(main_task))

        self.assertTrue(IPartOfSequentialProcess.providedBy(subtask))

        self.assertTrue(IPartOfSequentialProcess.providedBy(training_container))
        self.assertTrue(IContainParallelProcess.providedBy(training_container))

        self.assertTrue(IPartOfParallelProcess.providedBy(present_gever))
        self.assertTrue(IPartOfParallelProcess.providedBy(present_teamraum))

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

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
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

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
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
        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
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

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
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
        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
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

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
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

        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
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


def create_task(title="Task"):
    return {
        "title": title,
        "responsible": "fa:kathi.barfuss",
        "issuer": "kathi.barfuss",
        "deadline": "2022-03-04",
        "task_type": "direct-execution",
        "is_private": False
    }


def create_parallel_task_container(items, title="Parallel task"):
    return {
        "title": title,
        "sequence_type": "parallel",
        "items": items
    }


def create_sequential_task_container(items, title="Sequential task"):
    return {
        "title": title,
        "sequence_type": "sequential",
        "items": items
    }


def create_process(process):
    return {
        "related_documents": [],
        "start_immediately": False,
        "process": process
    }


def create_immediate_process(process):
    return {
        "related_documents": [],
        "start_immediately": True,
        "process": process
    }


class TestProcessInitialTaskStates(IntegrationTestCase):
    """This test class can be used to test all the different constellations
    of tasks and subtasks and its expected initial review states.
    """

    def run_process(self, data, browser):
        with self.observe_children(self.dossier) as children, freeze(datetime(2022, 2, 1)):
            browser.open('{}/@process'.format(
                         self.dossier.absolute_url()),
                         data=json.dumps(data),
                         headers=self.api_headers)

        return children['added'].pop()

    def create_states_dict(self, task):
        data = {
            'review_state': api.content.get_state(task),
        }
        items = [self.create_states_dict(content) for content in task.listFolderContents()]
        if items:
            data['items'] = items

        return data

    @browsing
    def test_flat_parallel_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_process(
            create_parallel_task_container([
                create_task(),
                create_task(),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {'review_state': TASK_STATE_OPEN},
                {'review_state': TASK_STATE_OPEN},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_flat_parallel_process_run_immediate(self, browser):
        self.login(self.regular_user, browser)

        data = create_immediate_process(
            create_parallel_task_container([
                create_task(),
                create_task(),
            ]))

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {'review_state': TASK_STATE_OPEN},
                {'review_state': TASK_STATE_OPEN},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_flat_sequential_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_process(
            create_sequential_task_container([
                create_task(),
                create_task(),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {'review_state': TASK_STATE_PLANNED},
                {'review_state': TASK_STATE_PLANNED},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_flat_sequential_process_run_immediate(self, browser):
        self.login(self.regular_user, browser)

        data = create_immediate_process(
            create_sequential_task_container([
                create_task(),
                create_task(),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {'review_state': TASK_STATE_OPEN},
                {'review_state': TASK_STATE_PLANNED},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_parallel_nested_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_process(
            create_parallel_task_container([
                create_parallel_task_container([
                    create_task(),
                    create_task(),
                ]),
                create_task(),
                create_task(),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_IN_PROGRESS,
                    'items': [
                        {'review_state': TASK_STATE_OPEN},
                        {'review_state': TASK_STATE_OPEN}
                    ]
                },
                {'review_state': TASK_STATE_OPEN},
                {'review_state': TASK_STATE_OPEN},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_parallel_nested_immediate_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_immediate_process(
            create_parallel_task_container([
                create_parallel_task_container([
                    create_task(),
                    create_task(),
                ]),
                create_task(),
                create_task(),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_IN_PROGRESS,
                    'items': [
                        {'review_state': TASK_STATE_OPEN},
                        {'review_state': TASK_STATE_OPEN}
                    ]
                },
                {'review_state': TASK_STATE_OPEN},
                {'review_state': TASK_STATE_OPEN},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_parallel_deep_nested_immediate_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_immediate_process(
            create_parallel_task_container([
                create_parallel_task_container([
                    create_parallel_task_container([
                        create_task(),
                        create_task(),
                    ]),
                    create_task(),
                ]),
                create_task(),
                create_task(),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_IN_PROGRESS,
                    'items': [
                        {
                            'review_state': TASK_STATE_IN_PROGRESS,
                            'items': [
                                {'review_state': TASK_STATE_OPEN},
                                {'review_state': TASK_STATE_OPEN}
                            ]
                        },
                        {'review_state': TASK_STATE_OPEN}
                    ]
                },
                {'review_state': TASK_STATE_OPEN},
                {'review_state': TASK_STATE_OPEN},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_sequential_nested_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_process(
            create_sequential_task_container([
                create_sequential_task_container([
                    create_task(),
                    create_task(),
                ]),
                create_task(),
                create_task(),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_PLANNED,
                    'items': [
                        {'review_state': TASK_STATE_PLANNED},
                        {'review_state': TASK_STATE_PLANNED}
                    ]
                },
                {'review_state': TASK_STATE_PLANNED},
                {'review_state': TASK_STATE_PLANNED},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_sequential_nested_immediate_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_immediate_process(
            create_sequential_task_container([
                create_sequential_task_container([
                    create_task(),
                    create_task(),
                ]),
                create_task(),
                create_task(),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_IN_PROGRESS,
                    'items': [
                        {'review_state': TASK_STATE_OPEN},
                        {'review_state': TASK_STATE_PLANNED}
                    ]
                },
                {'review_state': TASK_STATE_PLANNED},
                {'review_state': TASK_STATE_PLANNED},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_sequential_deep_nested_immediate_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_immediate_process(
            create_sequential_task_container([
                create_sequential_task_container([
                    create_sequential_task_container([
                        create_task(),
                        create_task(),
                    ]),
                    create_task(),
                ]),
                create_task(),
                create_task(),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_IN_PROGRESS,
                    'items': [
                        {
                            'review_state': TASK_STATE_OPEN,
                            'items': [
                                {'review_state': TASK_STATE_OPEN},
                                {'review_state': TASK_STATE_PLANNED}
                            ]
                        },
                        {'review_state': TASK_STATE_PLANNED}
                    ]
                },
                {'review_state': TASK_STATE_PLANNED},
                {'review_state': TASK_STATE_PLANNED},
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_deep_nested_parallel_sequential_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_process(
            create_parallel_task_container([
                create_sequential_task_container([
                    create_task(),
                    create_task(),
                ]),
                create_parallel_task_container([
                    create_parallel_task_container([
                        create_task(),
                        create_task(),
                    ]),
                    create_task(),
                ]),
                create_sequential_task_container([
                    create_task(),
                    create_task(),
                ]),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_PLANNED,
                    'items': [
                        {'review_state': TASK_STATE_PLANNED},
                        {'review_state': TASK_STATE_PLANNED}],
                },
                {
                    'review_state': TASK_STATE_IN_PROGRESS,
                    'items': [
                        {
                            'review_state': TASK_STATE_IN_PROGRESS,
                            'items': [
                                {'review_state': TASK_STATE_OPEN},
                                {'review_state': TASK_STATE_OPEN}
                            ],
                        },
                        {
                            'review_state': TASK_STATE_OPEN,
                        }
                    ],
                },
                {
                    'review_state': TASK_STATE_PLANNED,
                    'items': [
                        {'review_state': TASK_STATE_PLANNED},
                        {'review_state': TASK_STATE_PLANNED}
                    ],
                }
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_deep_nested_parallel_sequential_immediate_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_immediate_process(
            create_parallel_task_container([
                create_sequential_task_container([
                    create_task(),
                    create_task(),
                ]),
                create_parallel_task_container([
                    create_parallel_task_container([
                        create_task(),
                        create_task(),
                    ]),
                    create_task(),
                ]),
                create_sequential_task_container([
                    create_task(),
                    create_task(),
                ]),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_PLANNED,
                    'items': [
                        {'review_state': TASK_STATE_PLANNED},
                        {'review_state': TASK_STATE_PLANNED}],
                },
                {
                    'review_state': TASK_STATE_IN_PROGRESS,
                    'items': [
                        {
                            'review_state': TASK_STATE_IN_PROGRESS,
                            'items': [
                                {'review_state': TASK_STATE_OPEN},
                                {'review_state': TASK_STATE_OPEN}
                            ],
                        },
                        {
                            'review_state': TASK_STATE_OPEN,
                        }
                    ],
                },
                {
                    'review_state': TASK_STATE_PLANNED,
                    'items': [
                        {'review_state': TASK_STATE_PLANNED},
                        {'review_state': TASK_STATE_PLANNED}
                    ],
                }
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_deep_nested_sequential_parallel_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_process(
            create_sequential_task_container([
                create_parallel_task_container([
                    create_task(),
                    create_task(),
                ]),
                create_sequential_task_container([
                    create_parallel_task_container([
                        create_task(),
                        create_task(),
                    ]),
                    create_task(),
                ]),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_PLANNED,
                    'items': [
                        {'review_state': TASK_STATE_PLANNED},
                        {'review_state': TASK_STATE_PLANNED}],
                },
                {
                    'review_state': TASK_STATE_PLANNED,
                    'items': [
                        {
                            'review_state': TASK_STATE_PLANNED,
                            'items': [
                                {'review_state': TASK_STATE_PLANNED},
                                {'review_state': TASK_STATE_PLANNED}
                            ],
                        },
                        {
                            'review_state': TASK_STATE_PLANNED,
                        }
                    ],
                },
            ],
        }, self.create_states_dict(main_task))

    @browsing
    def test_deep_nested_sequential_parallel_immediate_process(self, browser):
        self.login(self.regular_user, browser)

        data = create_immediate_process(
            create_sequential_task_container([
                create_parallel_task_container([
                    create_task(),
                    create_task(),
                ]),
                create_sequential_task_container([
                    create_parallel_task_container([
                        create_task(),
                        create_task(),
                    ]),
                    create_task(),
                ]),
            ])
        )

        main_task = self.run_process(data, browser)

        self.assertDictEqual({
            'review_state': TASK_STATE_IN_PROGRESS,
            'items': [
                {
                    'review_state': TASK_STATE_IN_PROGRESS,
                    'items': [
                        {'review_state': TASK_STATE_OPEN},
                        {'review_state': TASK_STATE_OPEN}],
                },
                {
                    'review_state': TASK_STATE_PLANNED,
                    'items': [
                        {
                            'review_state': TASK_STATE_PLANNED,
                            'items': [
                                {'review_state': TASK_STATE_PLANNED},
                                {'review_state': TASK_STATE_PLANNED}
                            ],
                        },
                        {
                            'review_state': TASK_STATE_PLANNED,
                        }
                    ],
                },
            ],
        }, self.create_states_dict(main_task))
