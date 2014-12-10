from unittest2 import TestCase
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow


class SomethingWithWorkflow(object):

    def __init__(self, initial_state):
        self.workflow_state = initial_state


class TestUnitWorkflow(TestCase):

    def setUp(self):
        self.private = State('private', is_default=True)
        self.pending = State('pending')
        self.published = State('published')

        self.submit = Transition('private', 'pending')
        self.publish = Transition('pending', 'published')
        self.reject = Transition('pending', 'private')
        self.retract = Transition('published', 'pending')

        self.workflow = Workflow([
            self.private, self.pending, self.published
            ], [
            self.submit, self.publish, self.reject, self.retract
        ])

    def test_transition_string_representation(self):
        self.assertEqual('<Transition "private-pending">', str(self.submit))
        self.assertEqual('<Transition "private-pending">', repr(self.submit))

    def test_state_string_representation(self):
        self.assertEqual('<State "pending">', str(self.pending))
        self.assertEqual('<State "pending">', repr(self.pending))

    def test_default_workflow_is_set(self):
        self.assertEqual(self.private, self.workflow.default_state)

    def test_fails_without_default_workflow(self):
        with self.assertRaises(AssertionError):
            Workflow([self.pending], [])

    def test_fails_with_duplicate_state(self):
        with self.assertRaises(AssertionError):
            Workflow([self.private, self.private], [])

    def test_fails_with_duplicate_transition(self):
        with self.assertRaises(AssertionError):
            Workflow([self.private, self.pending], [self.submit, self.submit])

    def test_fails_with_invalid_transition(self):
        with self.assertRaises(AssertionError):
            Workflow([self.private, self.pending],
                     [Transition('private', 'invalid_identifier')])

    def test_get_state_returns_correct_state(self):
        self.assertEqual(self.private, self.workflow.get_state('private'))

    def test_get_state_fails_with_invalid_state(self):
        with self.assertRaises(KeyError):
            self.workflow.get_state('invalid_identifier')

    def test_can_execute_available_transition(self):
        obj = SomethingWithWorkflow(initial_state=self.private.name)
        self.assertTrue(
            self.workflow.can_execute_transition(obj, self.submit.name))

    def test_cannot_perform_unavailable_transition(self):
        obj = SomethingWithWorkflow(initial_state=self.private.name)
        self.assertFalse(
            self.workflow.can_execute_transition(obj, self.retract.name))

    def test_cannot_perform_invalid_transition(self):
        obj = SomethingWithWorkflow(initial_state=self.private.name)
        self.assertFalse(
            self.workflow.can_execute_transition(obj, 'invalid_name'))

    def test_performs_available_transition(self):
        obj = SomethingWithWorkflow(initial_state=self.pending.name)
        self.workflow.execute_transition(obj, self.publish.name)

        self.assertEqual(self.published.name, obj.workflow_state)

    def test_does_not_perform_unavailable_transition(self):
        obj = SomethingWithWorkflow(initial_state=self.pending.name)
        with self.assertRaises(AssertionError):
            self.workflow.execute_transition(obj, self.submit.name)

    def test_does_not_perform_invalid_transition(self):
        obj = SomethingWithWorkflow(initial_state=self.published.name)
        with self.assertRaises(AssertionError):
            self.workflow.execute_transition(obj, 'invalid_identifier')

    def test_transitions_are_registered_with_their_state(self):
        self.assertEqual([self.submit], self.private.get_transitions())
        self.assertEqual([self.publish, self.reject],
                         self.pending.get_transitions())
        self.assertEqual([self.retract], self.published.get_transitions())
