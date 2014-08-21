from opengever.globalindex import model
from opengever.globalindex import Session


def installed(site):
    model.Base.metadata.create_all(Session().bind)
