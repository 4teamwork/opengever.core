from opengever.ogds.base.utils import create_session
from opengever.ogds.base.model.user import User
from opengever.ogds.base.model.client import Client

MODELS = [User, Client]


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """

    # Only run step if a flag file is present
    if context.readDataFile('opengever.ogds.base.setuphandlers.txt') is None:
        return

    create_sql_tables()


def create_sql_tables():
    """Creates the sql tables for the models.
    """

    session = create_session()
    for model in MODELS:
        getattr(model, 'metadata').create_all(session.bind)
