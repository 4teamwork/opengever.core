from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity import base_notification_center
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.activity.roles import TODO_RESPONSIBLE_ROLE
from opengever.activity.roles import WORKSPACE_MEMBER_ROLE
from opengever.base.oguid import Oguid
from opengever.ogds.base.actor import ActorLookup
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from opengever.workspace.participation.storage import IInvitationStorage
from plone.protect import createToken
from zope.component import getUtility
import json


class TestToDoWatchers(IntegrationTestCase):

    features = ('activity', 'workspace')

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

        self.assertEqual([], self.center.get_watchers(self.todo))

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
    def test_new_workspace_member_is_watcher_on_all_todos_in_workspace(self, browser):
        self.login(self.workspace_owner, browser)

        workspace2 = create(Builder('workspace').within(self.workspace_root))
        todo_in_workspace2 = create(Builder('todo').within(workspace2))

        getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            self.meeting_user.getProperty('email'),
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        self.login(self.meeting_user, browser)
        my_invitations = browser.open(
            self.portal.absolute_url() + '/@my-workspace-invitations',
            method='GET',
            headers=self.api_headers,
            ).json

        watcher = self.center.fetch_watcher(self.meeting_user.getId())
        self.assertIsNone(watcher)

        # Accept invitation
        browser.open(
            my_invitations.get('items')[0].get('accept'),
            method='POST',
            headers=self.api_headers).json

        watcher = self.center.fetch_watcher(self.meeting_user.getId())
        self.assertIsNotNone(watcher)

        self.login(self.workspace_member, browser)

        watched_resources = [resource.oguid.resolve_object() for resource in watcher.resources]
        self.assertNotIn(todo_in_workspace2, watched_resources)
        self.assertItemsEqual(
            [self.todo, self.assigned_todo, self.completed_todo],
            watched_resources)

    @browsing
    def test_deleted_workspace_member_is_removed_as_watcher_from_all_contained_objects(self, browser):
        self.login(self.workspace_admin, browser=browser)
        self.center.add_watcher_to_resource(self.todo,
                                            self.workspace_member.getId(),
                                            WORKSPACE_MEMBER_ROLE)

        self.center.add_watcher_to_resource(self.workspace_document,
                                            self.workspace_member.getId(),
                                            WORKSPACE_MEMBER_ROLE)

        watcher = self.center.fetch_watcher(self.workspace_member.getId())
        subscriptions = watcher.subscriptions
        self.assertEqual(3, len(subscriptions))
        expected = [(TODO_RESPONSIBLE_ROLE, self.assigned_todo),
                    (WORKSPACE_MEMBER_ROLE, self.todo),
                    (WORKSPACE_MEMBER_ROLE, self.workspace_document)]
        actual = [(subscription.role, subscription.resource.oguid.resolve_object())
                  for subscription in subscriptions]
        self.assertItemsEqual(expected, actual)

        browser.open(self.workspace.absolute_url() + '/manage-participants/delete',
                     data={'token': self.workspace_member.getId(),
                           'type': 'user',
                           '_authenticator': createToken()})

        self.center.session.refresh(watcher)
        self.assertEqual([], watcher.subscriptions)

    @browsing
    def test_deleting_workspace_member_handles_missing_resources(self, browser):
        self.login(self.workspace_admin, browser=browser)

        base_center = base_notification_center()
        # create subscription for a resource with an invalid IntId.
        base_center.add_watcher_to_resource(Oguid('plone', 123),
                                            self.workspace_member.getId(),
                                            WORKSPACE_MEMBER_ROLE)

        watcher = self.center.fetch_watcher(self.workspace_member.getId())
        subscriptions = watcher.subscriptions
        self.assertEqual(2, len(subscriptions))

        expected = [Oguid.for_object(self.assigned_todo).id, 'plone:123']
        actual = [subscription.resource.oguid.id for subscription in subscriptions]
        self.assertItemsEqual(expected, actual)

        browser.open(self.workspace.absolute_url() + '/manage-participants/delete',
                     data={'token': self.workspace_member.getId(),
                           'type': 'user',
                           '_authenticator': createToken()})

        self.center.session.refresh(watcher)
        self.assertEqual([], watcher.subscriptions)


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
        self.assertEquals(u'To-do assigned', activity.label)
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
        self.assertEquals(u'To-do assigned', activity.label)
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

        browser.open(
            self.assigned_todo, method='POST', headers=self.api_headers,
            view="@workflow/opengever_workspace_todo--TRANSITION--complete--active_completed")

        activity = Activity.query.one()
        self.assertEquals('todo-modified', activity.kind)
        self.assertEquals(u'To-do closed', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals(u'Go live', activity.title)
        user = ActorLookup(self.workspace_owner.getId()).lookup()
        self.assertEquals(
            u'Closed by {}'.format(user.get_label(with_principal=False)),
            activity.summary)

    @browsing
    def test_reopened_activity_is_recorded_when_a_todo_is_reopened(self, browser):
        self.login(self.workspace_owner, browser)

        browser.open(
            self.completed_todo, method='POST', headers=self.api_headers,
            view="@workflow/opengever_workspace_todo--TRANSITION--open--completed_active")

        activity = Activity.query.one()
        self.assertEquals('todo-modified', activity.kind)
        self.assertEquals(u'To-do reopened', activity.label)
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
        self.assertEquals(u'To-do commented', activity.label)
        self.assertIsNone(activity.description)
        self.assertEquals('Fix user login', activity.title)
        user = ActorLookup(self.workspace_member.getId()).lookup()
        self.assertEquals(
            u'Commented by {}'.format(user.get_label(with_principal=False)),
            activity.summary)
