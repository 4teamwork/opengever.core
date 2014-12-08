from opengever.core.model import create_session
from opengever.meeting.model import Committee


def init_installed(site):
    session = create_session()
    create_example_committees(session)


def create_example_committees(session):
    for title in ['Gemeinderat', 'Informatikkommission']:
        session.add(Committee(title=title))
