from opengever.ogds.models import BASE
from opengever.ogds.models.declarative import query_base
from z3c.saconfig import named_scoped_session


Session = named_scoped_session('opengever')

BASE.session = Session
Base = query_base(Session)


def create_session():
    """Returns a new sql session bound to the defined named scope.
    """
    return Session()
