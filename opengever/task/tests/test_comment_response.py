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

    def test_commenting_is_disallowed_for_user_without_add_portal_content_permission(self):
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_roles('Reader')
               .with_userid('hugo.boss'))

        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        self.login('hugo.boss')

        self.assertFalse(ICommentResponseHandler(task).is_allowed())

    def test_commenting_is_allowed_if_user_has_add_portal_content_permission_and_dossier_is_not_closed(self):
        dossier = create(Builder('dossier'))
        task = create(Builder('task').within(dossier))

        self.assertTrue(ICommentResponseHandler(task).is_allowed())

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
