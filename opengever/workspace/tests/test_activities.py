from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.activity.roles import TODO_RESPONSIBLE_ROLE
from opengever.activity.roles import WORKSPACE_MEMBER_ROLE
from opengever.ogds.base.actor import ActorLookup
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from opengever.workspace.participation.storage import IInvitationStorage
from unittest import skip
from zope.component import getUtility
import json


class TestToDoWatchers(IntegrationTestCase):

    features = ('activity', )

    def setUp(self):
        super(TestToDoWatchers, self).setUp()
        # Because the activity is not setup during creation of the fixture
        # there is no responsible set as watcher on the assigned_todo, which
        # we correct here
        self.center = notification_center()

        with self.login(self.workspace_member):
            self.center.add_watcher_to_resource(self.assigned_todo,
                                                self.assigned_todo.responsible,
                                                TODO_RESPONSIBLE_ROLE)

    def test_responsible_is_registered_as_watcher_when_todo_is_created(self):
        self.login(self.workspace_owner)
        todo = create(
                    Builder('todo')
                    .titled(u'Test ToDos')
                    .having(responsible=self.workspace_member.getId())
                    .within(self.workspace)
                    )

        resource = self.center.fetch_resource(todo)

        responsible_watchers = [
            sub.watcher.actorid for sub in resource.subscriptions
            if sub.role == TODO_RESPONSIBLE_ROLE]

        self.assertItemsEqual([self.workspace_member.getId()], responsible_watchers)

    def test_workspace_users_are_registered_as_watcher_when_todo_is_created(self):
        self.login(self.workspace_owner)
        todo = create(
                    Builder('todo')
                    .titled(u'Test ToDos')
                    .within(self.workspace)
                    )

        resource = self.center.fetch_resource(todo)

        watchers = [
            sub.watcher.actorid for sub in resource.subscriptions
            if sub.role == WORKSPACE_MEMBER_ROLE]

        participants = ManageParticipants(self.workspace, self.request).get_participants()
        self.assertItemsEqual([participant["userid"] for participant in participants],
                              watchers)

    @browsing
    def test_responsible_is_registered_as_watcher_when_todo_is_assigned(self, browser):
        self.login(self.workspace_owner, browser)

        self.assertEqual(tuple(), self.center.get_watchers(self.todo))

        # Assigning a responsible adds him as watcher
        browser.open(self.todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'responsible': self.workspace_guest.getId()}))

        subscriptions = self.center.fetch_resource(self.todo).subscriptions
        responsible_watchers = [
            sub.watcher.actorid for sub in subscriptions
            if sub.role == TODO_RESPONSIBLE_ROLE]

        self.assertItemsEqual([self.workspace_guest.getId()], responsible_watchers)

    @browsing
    def test_responsible_watcher_is_updated_when_todo_is_reassigned(self, browser):
        self.login(self.workspace_owner, browser)

        subscriptions = self.center.fetch_resource(self.assigned_todo).subscriptions
        responsible_watchers = [
            sub.watcher.actorid for sub in subscriptions
            if sub.role == TODO_RESPONSIBLE_ROLE]

        self.assertItemsEqual([self.workspace_member.getId()], responsible_watchers)

        # Reassigning a todo, replaces the responsible watcher.
        browser.open(self.assigned_todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'responsible': self.workspace_guest.getId()}))

        subscriptions = self.center.fetch_resource(self.assigned_todo).subscriptions
        responsible_watchers = [
            sub.watcher.actorid for sub in subscriptions
            if sub.role == TODO_RESPONSIBLE_ROLE]

        self.assertItemsEqual([self.workspace_guest.getId()], responsible_watchers)

    @skip("This fails because of a but in plone.restapi, "
          "see https://github.com/4teamwork/opengever.core/issues/5902")
    @browsing
    def test_responsible_watcher_is_updated_when_todo_is_unassigned(self, browser):
        self.login(self.workspace_owner, browser)

        browser.open(self.assigned_todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'responsible': None}))

        subscriptions = self.center.fetch_resource(self.assigned_todo).subscriptions
        responsible_watchers = [
            sub.watcher.actorid for sub in subscriptions
            if sub.role == TODO_RESPONSIBLE_ROLE]

        self.assertEqual([], responsible_watchers)

    @browsing
    def test_new_workspace_member_is_watcher_on_all_todos(self, browser):
        self.login(self.workspace_owner, browser)

        getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            self.regular_user.getId(),
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        self.login(self.regular_user, browser)
        my_invitations = browser.open(
            self.portal.absolute_url() + '/@my-workspace-invitations',
            method='GET',
            headers=self.api_headers,
            ).json

        watcher = self.center.fetch_watcher(self.regular_user.getId())
        self.assertIsNone(watcher)

        # Accept invitation
        browser.open(
            my_invitations.get('items')[0].get('accept'),
            method='POST',
            headers=self.api_headers).json

        watcher = self.center.fetch_watcher(self.regular_user.getId())
        self.assertIsNotNone(watcher)

        self.login(self.workspace_member, browser)
        self.assertItemsEqual(
            [self.todo, self.assigned_todo, self.completed_todo],
            [resource.oguid.resolve_object() for resource in watcher.resources])


class TestToDoActivities(IntegrationTestCase):

    features = ('activity', )

    def test_assigned_activity_is_recorded_when_a_todo_with_responsible_is_created(self):
        self.login(self.workspace_owner)
        create(Builder('todo')
               .titled(u'Test ToDos')
               .having(responsible=self.workspace_member.getId())
               .within(self.workspace))

        activity = Activity.query.one()
        self.assertEquals('todo-assigned', activity.kind)
        self.assertEquals(u'ToDo assigned', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals(u'Test ToDos', activity.title)
        user = ActorLookup(self.workspace_owner.getId()).lookup()
        responsible = ActorLookup(self.workspace_member.getId()).lookup()
        self.assertEquals(
            u'Assigned to {} by {}'.format(
                responsible.get_label(with_principal=False),
                user.get_label(with_principal=False)),
            activity.summary)

    @browsing
    def test_assigned_activity_is_recorded_when_a_todo_is_reassigned(self, browser):
        self.login(self.workspace_owner, browser)

        browser.open(self.assigned_todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'responsible': self.workspace_guest.getId()}))

        activity = Activity.query.one()
        self.assertEquals('todo-assigned', activity.kind)
        self.assertEquals(u'ToDo assigned', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals(u'Go live', activity.title)
        user = ActorLookup(self.workspace_owner.getId()).lookup()
        responsible = ActorLookup(self.workspace_guest.getId()).lookup()
        self.assertEquals(
            u'Assigned to {} by {}'.format(
                responsible.get_label(with_principal=False),
                user.get_label(with_principal=False)),
            activity.summary)

    @browsing
    def test_closed_activity_is_recorded_when_a_todo_is_closed(self, browser):
        self.login(self.workspace_owner, browser)

        browser.open(self.assigned_todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'completed': True}))

        activity = Activity.query.one()
        self.assertEquals('todo-modified', activity.kind)
        self.assertEquals(u'ToDo closed', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals(u'Go live', activity.title)
        user = ActorLookup(self.workspace_owner.getId()).lookup()
        self.assertEquals(
            u'Closed by {}'.format(user.get_label(with_principal=False)),
            activity.summary)

    @browsing
    def test_reopened_activity_is_recorded_when_a_todo_is_reopened(self, browser):
        self.login(self.workspace_owner, browser)

        browser.open(self.completed_todo, method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'completed': False}))

        activity = Activity.query.one()
        self.assertEquals('todo-modified', activity.kind)
        self.assertEquals(u'ToDo reopened', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals(u'Cleanup installation', activity.title)
        user = ActorLookup(self.workspace_owner.getId()).lookup()
        self.assertEquals(
            u'Reopened by {}'.format(user.get_label(with_principal=False)),
            activity.summary)

    @browsing
    def test_commented_activity_is_recorded_when_a_todo_is_commented(self, browser):
        self.login(self.workspace_member, browser)

        url = '{}/@responses'.format(self.todo.absolute_url())
        browser.open(url, method="POST", headers=self.api_headers,
                     data=json.dumps({'text': u'Angebot \xfcberpr\xfcft'}))

        activity = Activity.query.one()
        self.assertEquals('todo-modified', activity.kind)
        self.assertEquals(u'ToDo commented', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals('Fix user login', activity.title)
        user = ActorLookup(self.workspace_member.getId()).lookup()
        self.assertEquals(
            u'Commented by {}'.format(user.get_label(with_principal=False)),
            activity.summary)
