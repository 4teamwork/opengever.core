
class PreconditionsViolated(Exception):
    """One or more preconditions for a workflow transition have been violated.
    """

    def __init__(self, errors):
        self.errors = errors
