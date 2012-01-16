from ftw.testing import MockTestCase
from mocker import ANY
from opengever.task.browser import complete


class TestCompleteTaskView(MockTestCase):

    def setUp(self):
        self.portal_membership = self.stub()
        self.mock_tool(self.portal_membership, 'portal_membership')

        self.expect(self.portal_membership.checkPermission(
                'Add portal content', ANY)).result(True)

    def test_use_success_form_checks_permissions(self):
        context = self.stub()
        request = self.stub()

        self.expect(self.portal_membership.checkPermission(
                'Add portal content', context)).result(False).count(1)

        self.replay()
        view = complete.CompleteTask(context, request)

        self.assertFalse(view.use_successor_form('transition'))

    def test_use_successor_form_checks_predecessor(self):
        context = self.mocker.mock()
        request = self.stub()

        self.expect(context.predecessor).result(None)

        self.replay()
        view = complete.CompleteTask(context, request)

        self.assertFalse(view.use_successor_form('transition'))

    def test_use_successor_form_transitions(self):
        context = self.create_dummy(predecessor=u'client1:123')
        request = self.stub()

        self.replay()
        view = complete.CompleteTask(context, request)
        use = view.use_successor_form

        # UNIDIRECTIONAL
        transitions = {
            'task-transition-cancelled-open': False,
            'task-transition-in-progress-resolved': False,
            'task-transition-in-progress-tested-and-closed': True,
            'task-transition-open-cancelled': False,
            'task-transition-open-in-progress': False,
            'task-transition-open-rejected': False,
            'task-transition-open-resolved': False,
            'task-transition-open-tested-and-closed': True,
            'task-transition-reassign': False,
            'task-transition-rejected-open': False,
            'task-transition-resolved-open': False,
            'task-transition-resolved-tested-and-closed': True
            }

        for type_cat in ('unidirectional_by_reference',
                         'unidirectional_by_value'):
            context.task_type_category = type_cat

            for transition, expected in transitions.items():
                result = use(transition)
                assert result == expected, \
                    'Wrong result %s (expected %s for %s / %s)' % (
                    result, expected, transition, context.task_type_category)

        # BIDIRECTIONAL
        transitions = {
            'task-transition-cancelled-open': False,
            'task-transition-in-progress-resolved': True,
            'task-transition-in-progress-tested-and-closed': False,
            'task-transition-open-cancelled': False,
            'task-transition-open-in-progress': False,
            'task-transition-open-rejected': False,
            'task-transition-open-resolved': True,
            'task-transition-open-tested-and-closed': False,
            'task-transition-reassign': False,
            'task-transition-rejected-open': False,
            'task-transition-resolved-open': False,
            'task-transition-resolved-tested-and-closed': False
            }

        for type_cat in ('bidirectional_by_reference',
                         'bidirectional_by_value'):
            context.task_type_category = type_cat

            for transition, expected in transitions.items():
                result = use(transition)
                assert result == expected, \
                    'Wrong result %s (expected %s for %s / %s)' % (
                    result, expected, transition, context.task_type_category)

    def render_fails_with_no_transition(self):
        context = self.stub()
        request = self.mocker.mock()

        self.expect(request.get('transition', None)).result(None)

        self.replay()
        view = complete.CompleteTask(context, request)

        with self.assertRaises() as cm:
            view.render()

        self.assertEqual(str(cm.exception),
                         'Bad request: could not find transition in request')

    def render_redirects_to_direct_response_if_no_successor_form(self):
        context = self.stub()
        request = self.mocker.mock()

        # makes use_successor_form return False
        self.expect(context.predecessor).result(False)

        self.expect(request.get('transition', None)).result('foo').count(
            0, None)

        self.expect(context.absolute_url()).result('http://nohost/mytask')
        self.expect(request.RESPONSE.redirect(
                'http://nohost/mytask/direct_response?form.widgets.'
                'transition=foo'))

        self.replay()
        view = complete.CompleteTask(context, request)
        view.render()
