from opengever.globalindex import model
from opengever.globalindex import Session


def create_tables(context):
    if context.readDataFile('opengever.globalindex_various.txt') is None:
        return
    session = Session()
    model.Base.metadata.create_all(session.bind)
