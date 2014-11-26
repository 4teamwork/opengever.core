from opengever.ogds.base.utils import Session
from opengever.ogds.models import BASE
from opengever.ogds.models.declarative import query_base

BASE.session = Session
Base = query_base(Session)
