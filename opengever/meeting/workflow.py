class State(object):

    def __init__(self, name, is_default=False, title=None):
        self.name = name
        self.transitions = []
        self.is_default = is_default
        self.title = title or name

    def register_transition(self, transition):
        self.transitions.append(transition)

    def get_transitions(self):
        return self.transitions

    def __repr__(self):
        return '<State "{}">'.format(self.name)


class Transition(object):

    def __init__(self, state_from, state_to, title=None):
        self.state_from = state_from
        self.state_to = state_to
        self.title = title or self.name

    @property
    def name(self):
        return '-'.join((self.state_from, self.state_to))

    def execute(self, obj, model):
        assert self.can_execute(model)
        model.workflow_state = self.state_to

    def can_execute(self, model):
        return model.workflow_state == self.state_from

    def __repr__(self):
        return '<Transition "{}">'.format(self.name)


class Workflow(object):

    def __init__(self, states, transitions):
        self.default_state = None
        self.states = {}
        for state in states:
            if state.is_default:
                assert self.default_state is None, 'only one default state is allowed'
                self.default_state = state
            self.states[state.name] = state
        assert self.default_state, 'missing default state'

        self.transitions = {}
        for transition in transitions:
            assert transition.name not in self.transitions
            state_from = self.states.get(transition.state_from)
            assert self.states.get(transition.state_to), 'no such state: {}'.format(transition.state_to)
            assert state_from, 'no such state: {}'.format(transition.state_from)

            self.transitions[transition.name] = transition
            state_from.register_transition(transition)

    def get_state(self, name):
        return self.states[name]

    def execute_transition(self, obj, model, name):
        transition = self.transitions.get(name)
        assert transition, 'no such transition: {}'.format(name)
        transition.execute(obj, model)

    def can_execute_transition(self, model, name):
        transition = self.transitions.get(name)
        return transition is not None and transition.can_execute(model)
