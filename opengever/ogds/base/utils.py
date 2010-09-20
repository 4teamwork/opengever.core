from z3c.saconfig import named_scoped_session


Session = named_scoped_session('opengever.ogds')


def create_session():
    """Returns a new sql session bound to the defined named scope.
    """

    return Session()
