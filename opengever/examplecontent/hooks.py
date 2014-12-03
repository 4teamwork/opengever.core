from opengever.core.model import create_session
from opengever.meeting.model import Commission


def init_installed(site):
    session = create_session()
    create_example_commissions(session)


def create_example_commissions(session):
    for title in ['Gemeinderat', 'Informatikkommission']:
        session.add(Commission(title=title))
