from datetime import date
from datetime import timedelta
from opengever.base.model import create_session
from opengever.meeting.model import Member
from opengever.meeting.model import Membership


def create_example_meeting_content(site):
    session = create_session()
    committee = site['sitzungen']['committee-1']
    committee_model = committee.load_model()

    peter = Member(firstname=u'Peter', lastname=u'M\xfcller')
    session.add(peter)
    hans = Member(firstname=u'Hans', lastname=u'Meier')
    session.add(hans)

    peter_membership = Membership(
        committee=committee_model,
        member=peter,
        date_from=date.today(),
        date_to=date.today() + timedelta(days=512))
    session.add(peter_membership)

    hans_membership = Membership(
        committee=committee_model,
        member=hans,
        date_from=date.today(),
        date_to=date.today() + timedelta(days=512))
    session.add(hans_membership)


def init_profile_installed(site):
    create_example_meeting_content(site)
