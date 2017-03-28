from ftw.builder import Builder
from ftw.builder import create
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.task.adapters import IResponseContainer
from opengever.task.comment_response import CommentResponseHandler
from opengever.task.interfaces import ICommentResponseHandler
from opengever.testing import FunctionalTestCase
from zope.interface.verify import verifyClass


class TestCommentResponseHandler(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def test_verify_interfaces(self):
        verifyClass(ICommentResponseHandler, CommentResponseHandler)

    def test_commenting_is_disallowed_for_tasks_within_a_closed_dossier(self):
        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        task = create(Builder('task')
                      .within(dossier))

        self.assertFalse(ICommentResponseHandler(task).is_allowed())

    def test_add_response_creates_a_task_commented_activity_record(self):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        ICommentResponseHandler(task).add_response("My response")

        activity = Activity.query.one()
        self.assertEquals('task-commented', activity.kind)

    def test_add_response_appends_a_new_response_obj_to_the_context_response_container(self):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        response_container = IResponseContainer(task)

        self.assertEqual(0, len(response_container))
        ICommentResponseHandler(task).add_response("My response")
        self.assertEqual(1, len(response_container))

    def test_a_Member_can_not_add_task_comment_on_open_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Member')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertFalse(ICommentResponseHandler(task).is_allowed())

    def test_a_Reader_can_not_add_task_comment_on_open_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Reader')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertFalse(ICommentResponseHandler(task).is_allowed())

    def test_a_Editor_can_add_task_comment_on_open_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Editor')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertTrue(ICommentResponseHandler(task).is_allowed())

    def test_a_Contributor_can_add_task_comment_on_open_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Contributor')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertTrue(ICommentResponseHandler(task).is_allowed())

    def test_a_Administrator_can_add_task_comment_on_open_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Administrator')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertTrue(ICommentResponseHandler(task).is_allowed())

    def test_a_Manager_can_add_task_comment_on_open_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Manager')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertTrue(ICommentResponseHandler(task).is_allowed())

    def test_a_Member_can_not_add_task_comment_on_closed_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Member')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertFalse(ICommentResponseHandler(task).is_allowed())

    def test_a_Reader_can_not_add_task_comment_on_closed_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Reader')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertFalse(ICommentResponseHandler(task).is_allowed())

    def test_a_Editor_can_not_add_task_comment_on_closed_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Editor')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertFalse(ICommentResponseHandler(task).is_allowed())

    def test_a_Contributor_can_not_add_task_comment_on_closed_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Contributor')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertFalse(ICommentResponseHandler(task).is_allowed())

    def test_a_Administrator_can_not_add_task_comment_on_closed_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Administrator')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertFalse(ICommentResponseHandler(task).is_allowed())

    def test_a_Manager_can_not_add_task_comment_on_closed_dossier(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Manager')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertFalse(ICommentResponseHandler(task).is_allowed())
